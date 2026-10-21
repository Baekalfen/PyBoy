#include <torch/extension.h>
#include <pybind11/numpy.h>
#include <ATen/mps/MPSAllocatorInterface.h>
#include <ATen/mps/MPSStream.h>
#include <Metal/Metal.h>
#include <Foundation/Foundation.h>
#include <QuartzCore/CAMetalLayer.h>

#include <cstdint>
#include <stdexcept>
#include <string>

namespace py = pybind11;

static id<MTLBuffer> tensor_buffer(const torch::Tensor& tensor) {
    TORCH_CHECK(tensor.device().type() == torch::kMPS, "Metal renderer inputs must be MPS tensors");
    TORCH_CHECK(tensor.is_contiguous(), "Metal renderer inputs must be contiguous");
    return (__bridge id<MTLBuffer>)tensor.storage().data();
}

class MetalFrameRenderer {
 public:
    explicit MetalFrameRenderer(const std::string& shader_source) {
        device_ = MTLCreateSystemDefaultDevice();
        TORCH_CHECK(device_ != nil, "No Metal device is available");

        NSString* source = [[NSString alloc]
            initWithBytes:shader_source.data()
                   length:shader_source.size()
                 encoding:NSUTF8StringEncoding];
        TORCH_CHECK(source != nil, "Metal shader source is not valid UTF-8");

        NSError* error = nil;
        id<MTLLibrary> library = [device_ newLibraryWithSource:source options:nil error:&error];
        TORCH_CHECK(
            library != nil,
            "Failed to compile PyBoy Metal shader: ",
            error == nil ? "unknown Metal compiler error" : error.localizedDescription.UTF8String
        );

        id<MTLFunction> function = [library newFunctionWithName:@"render_frame"];
        TORCH_CHECK(function != nil, "Metal shader is missing render_frame");
        pipeline_ = [device_ newComputePipelineStateWithFunction:function error:&error];
        TORCH_CHECK(
            pipeline_ != nil,
            "Failed to create PyBoy Metal pipeline: ",
            error == nil ? "unknown pipeline error" : error.localizedDescription.UTF8String
        );

        id<MTLFunction> present_function = [library newFunctionWithName:@"present_frame"];
        TORCH_CHECK(present_function != nil, "Metal shader is missing present_frame");
        present_pipeline_ = [device_ newComputePipelineStateWithFunction:present_function error:&error];
        TORCH_CHECK(
            present_pipeline_ != nil,
            "Failed to create PyBoy Metal presentation pipeline: ",
            error == nil ? "unknown pipeline error" : error.localizedDescription.UTF8String
        );
    }

    void render(
        const torch::Tensor& memory,
        py::array_t<uint8_t, py::array::c_style> scanlines,
        py::array_t<int32_t, py::array::c_style> config,
        const torch::Tensor& frame
    ) {
        TORCH_CHECK(memory.numel() == 8192 * 2 + 160, "Combined VRAM/OAM input has an invalid size");
        TORCH_CHECK(memory.device().is_cpu() && memory.is_pinned(), "Renderer input must use pinned host memory");
        TORCH_CHECK(scanlines.size() == 144 * 5, "Scanline input must contain 144 five-byte records");
        const uint8_t* scanline_data = scanlines.data();
        TORCH_CHECK(config.size() == 83, "Renderer configuration must contain 83 integers");
        TORCH_CHECK(frame.numel() == 144 * 160 * 4, "Output must contain one RGBA frame");

        void* pinned_buffer = at::mps::getMPSPinnedMTLBuffer(memory.data_ptr());
        TORCH_CHECK(pinned_buffer != nullptr, "Pinned input tensor has no MPS-visible Metal buffer");
        id<MTLBuffer> memory_buffer = (__bridge id<MTLBuffer>)pinned_buffer;
        id<MTLBuffer> frame_buffer = tensor_buffer(frame);
        const int32_t* config_data = config.data();

        at::mps::MPSStream* stream = at::mps::getCurrentMPSStream();
        TORCH_CHECK(stream != nullptr, "PyTorch did not provide a current MPS stream");
        id<MTLComputePipelineState> pipeline = pipeline_;

        at::mps::dispatch_sync_with_rethrow(stream->queue(), ^{
            stream->endKernelCoalescing();
            id<MTLCommandBuffer> command_buffer = stream->commandBuffer();
            id<MTLComputeCommandEncoder> encoder = [command_buffer computeCommandEncoder];
            [encoder setComputePipelineState:pipeline];
            [encoder setBuffer:memory_buffer offset:0 atIndex:0];
            [encoder setBuffer:memory_buffer offset:8192 atIndex:1];
            [encoder setBuffer:memory_buffer offset:16384 atIndex:2];
            [encoder setBytes:scanline_data length:scanlines.nbytes() atIndex:3];
            [encoder setBytes:config_data length:config.nbytes() atIndex:4];
            [encoder setBuffer:frame_buffer offset:0 atIndex:5];

            MTLSize grid = MTLSizeMake(160, 144, 1);
            MTLSize group = MTLSizeMake(160, 1, 1);
            [encoder dispatchThreads:grid threadsPerThreadgroup:group];
            [encoder endEncoding];
        });
        stream->synchronize(at::mps::SyncType::COMMIT);
    }

    void present(const torch::Tensor& frame, uintptr_t layer_address) {
        TORCH_CHECK(frame.device().type() == torch::kMPS, "Metal presentation requires an MPS tensor");
        TORCH_CHECK(frame.is_contiguous(), "Metal presentation input must be contiguous");
        TORCH_CHECK(frame.numel() == 144 * 160 * 4, "Metal presentation input must contain one RGBA frame");
        TORCH_CHECK(layer_address != 0, "Metal presentation requires a valid CAMetalLayer");

        CAMetalLayer* layer = (__bridge CAMetalLayer*)reinterpret_cast<void*>(layer_address);
        TORCH_CHECK(layer != nil, "Metal presentation received an invalid CAMetalLayer");
        if (layer.device != device_) {
            layer.device = device_;
        }
        if (layer.pixelFormat != MTLPixelFormatBGRA8Unorm) {
            layer.pixelFormat = MTLPixelFormatBGRA8Unorm;
        }
        if (layer.framebufferOnly) {
            layer.framebufferOnly = NO;
        }

        id<CAMetalDrawable> drawable = [layer nextDrawable];
        TORCH_CHECK(drawable != nil, "SDL Metal window did not provide a drawable");
        id<MTLTexture> texture = drawable.texture;
        id<MTLBuffer> frame_buffer = tensor_buffer(frame);

        at::mps::MPSStream* stream = at::mps::getCurrentMPSStream();
        TORCH_CHECK(stream != nullptr, "PyTorch did not provide a current MPS stream");
        id<MTLComputePipelineState> pipeline = present_pipeline_;

        at::mps::dispatch_sync_with_rethrow(stream->queue(), ^{
            stream->endKernelCoalescing();
            id<MTLCommandBuffer> command_buffer = stream->commandBuffer();
            id<MTLComputeCommandEncoder> encoder = [command_buffer computeCommandEncoder];
            [encoder setComputePipelineState:pipeline];
            [encoder setBuffer:frame_buffer offset:0 atIndex:0];
            [encoder setTexture:texture atIndex:0];

            MTLSize grid = MTLSizeMake(texture.width, texture.height, 1);
            MTLSize group = MTLSizeMake(16, 16, 1);
            [encoder dispatchThreads:grid threadsPerThreadgroup:group];
            [encoder endEncoding];
            [command_buffer presentDrawable:drawable];
        });
        stream->synchronize(at::mps::SyncType::COMMIT);
    }

 private:
    __strong id<MTLDevice> device_ = nil;
    __strong id<MTLComputePipelineState> pipeline_ = nil;
    __strong id<MTLComputePipelineState> present_pipeline_ = nil;
};

PYBIND11_MODULE(TORCH_EXTENSION_NAME, module) {
    py::class_<MetalFrameRenderer>(module, "MetalFrameRenderer")
        .def(py::init<const std::string&>())
        .def(
            "render",
            &MetalFrameRenderer::render,
            py::arg("memory"),
            py::arg("scanlines"),
            py::arg("config"),
            py::arg("frame")
        )
        .def("present", &MetalFrameRenderer::present, py::arg("frame"), py::arg("layer_address"));
}
