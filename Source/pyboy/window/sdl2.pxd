# Cython PXD file for SDL2 2.0.3

# Wrapped headers:
#  - SDL_stdinc.h (partial)
#  - SDL.h
#  - SDL_version.h
#  - SDL_revision.h
#  - SDL_error.h
#  - SDL_rwops.h (partial)
#  - SDL_timer.h
#  - SDL_rect.h
#  - SDL_pixels.h
#  - SDL_blendmode.h
#  - SDL_surface.h
#  - SDL_video.h
#  - SDL_render.h
#  - SDL_audio.h
#  - SDL_scancode.h
#  - SDL_keycode.h
#  - SDL_keyboard.h
#  - SDL_mouse.h
#  - SDL_joystick.h
#  - SDL_gamecontroller.h
#  - SDL_touch.h
#  - SDL_gesture.h
#  - SDL_events.h
#  - SDL_hints.h
#  - SDL_platform.h

cdef extern from "SDL_stdinc.h" nogil:

    ctypedef enum SDL_bool:
        SDL_TRUE
        SDL_FALSE

    ctypedef signed char Sint8
    ctypedef unsigned char Uint8
    ctypedef signed short Sint16
    ctypedef unsigned short Uint16
    ctypedef signed long Sint32
    ctypedef unsigned long Uint32
    ctypedef signed long long Sint64
    ctypedef unsigned long long Uint64

cdef extern from "SDL.h" nogil:

    Uint32 SDL_INIT_TIMER
    Uint32 SDL_INIT_AUDIO
    Uint32 SDL_INIT_VIDEO
    Uint32 SDL_INIT_JOYSTICK
    Uint32 SDL_INIT_HAPTIC
    Uint32 SDL_INIT_GAMECONTROLLER
    Uint32 SDL_INIT_EVENTS
    Uint32 SDL_INIT_NOPARACHUTE
    Uint32 SDL_INIT_EVERYTHING

    int SDL_Init(Uint32 flags)
    int SDL_InitSubSystem(Uint32 flags)
    void SDL_QuitSubSystem(Uint32 flags)
    Uint32 SDL_WasInit(Uint32 flags)
    void SDL_Quit()

cdef extern from "SDL_version.h" nogil:

    ctypedef struct SDL_version:
        Uint8 major
        Uint8 minor
        Uint8 patch

    int SDL_MAJOR_VERSION # macro
    int SDL_MINOR_VERSION # macro
    int SDL_PATCHLEVEL # macro

    void SDL_VERSION(SDL_version* x) # macro
    int SDL_VERSIONNUM(int x, int y, int z) # macro
    int SDL_COMPILEDVERSION() # macro
    int SDL_VERSION_ATLEAST(int x, int y, int z) # macro
    void SDL_GetVersion(SDL_version* ver)
    const char* SDL_GetRevision()
    int SDL_GetRevisionNumber()

cdef extern from "SDL_revision.h" nogil:

    const char* SDL_REVISION # macro
    int SDL_REVISION_NUMBER # macro

cdef extern from "SDL_error.h" nogil:

    int SDL_SetError(const char* fmt, ...)
    const char* SDL_GetError()
    void SDL_ClearError()

    ctypedef enum SDL_errorcode:
        SDL_ENOMEM
        SDL_EFREAD
        SDL_EFWRITE
        SDL_EFSEEK
        SDL_UNSUPPORTED
        SDL_LASTERROR

    int SDL_Error(SDL_errorcode code)
    int SDL_OutOfMemory() # macro
    int SDL_Unsupported() # macro
    int SDL_InvalidParamError() # macro

cdef extern from "SDL_rwops.h" nogil:

    ctypedef struct SDL_RWops:
        pass

cdef extern from "SDL_timer.h" nogil:

    Uint32 SDL_GetTicks()
    int SDL_TICKS_PASSED(int A, int B) # macro
    Uint64 SDL_GetPerformanceCounter()
    Uint64 SDL_GetPerformanceFrequency()
    void SDL_Delay(Uint32 ms)

    ctypedef Uint32 (*SDL_TimerCallback) (Uint32 interval, void* param)
    ctypedef int SDL_TimerID

    SDL_TimerID SDL_AddTimer(Uint32 interval, SDL_TimerCallback callback, void* param)
    SDL_bool SDL_RemoveTimer(SDL_TimerID id)

cdef extern from "SDL_rect.h" nogil:

    ctypedef struct SDL_Point:
        int x
        int y

    ctypedef struct SDL_Rect:
        int x, y
        int w, h

    SDL_bool SDL_RectEmpty(const SDL_Rect* r)
    SDL_bool SDL_RectEquals(const SDL_Rect* a, const SDL_Rect* b)
    SDL_bool SDL_HasIntersection(const SDL_Rect* A, const SDL_Rect* B)
    SDL_bool SDL_IntersectRect(const SDL_Rect* A, const SDL_Rect* B, SDL_Rect* result)
    void SDL_UnionRect(const SDL_Rect* A, const SDL_Rect* B, SDL_Rect* result)
    SDL_bool SDL_EnclosePoints(const SDL_Point* points, int count, const SDL_Rect* clip, SDL_Rect* result)
    SDL_bool SDL_IntersectRectAndLine(const SDL_Rect* rect, int* X1, int* Y1, int* X2, int* Y2)

cdef extern from "SDL_pixels.h" nogil:

    ctypedef struct SDL_Color:
        Uint8 r
        Uint8 g
        Uint8 b
        Uint8 a

    ctypedef SDL_Color SDL_Colour # macro

    ctypedef struct SDL_Palette:
        int ncolors
        SDL_Color* colors
        Uint32 version
        int refcount

    ctypedef struct SDL_PixelFormat:
        Uint32 format
        SDL_Palette* palette
        Uint8 BitsPerPixel
        Uint8 BytesPerPixel
        Uint8 padding[2]
        Uint32 Rmask
        Uint32 Gmask
        Uint32 Bmask
        Uint32 Amask
        Uint8 Rloss
        Uint8 Gloss
        Uint8 Bloss
        Uint8 Aloss
        Uint8 Rshift
        Uint8 Gshift
        Uint8 Bshift
        Uint8 Ashift
        int refcount
        SDL_PixelFormat* next

    const char* SDL_GetPixelFormatName(Uint32 format)
    SDL_bool SDL_PixelFormatEnumToMasks(Uint32 format, int* bpp, Uint32* Rmask, Uint32* Gmask, Uint32* Bmask, Uint32* Amask)
    Uint32 SDL_MasksToPixelFormatEnum(int bpp, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask)
    SDL_PixelFormat* SDL_AllocFormat(Uint32 pixel_format)
    void  SDL_FreeFormat(SDL_PixelFormat* format)
    SDL_Palette* SDL_AllocPalette(int ncolors)
    int SDL_SetPixelFormatPalette(SDL_PixelFormat* format, SDL_Palette* palette)
    int SDL_SetPaletteColors(SDL_Palette* palette, const SDL_Color* colors, int firstcolor, int ncolors)
    void SDL_FreePalette(SDL_Palette* palette)
    Uint32 SDL_MapRGB(const SDL_PixelFormat* format, Uint8 r, Uint8 g, Uint8 b)
    Uint32 SDL_MapRGBA(const SDL_PixelFormat* format, Uint8 r, Uint8 g, Uint8 b, Uint8 a)
    void SDL_GetRGB(Uint32 pixel, const SDL_PixelFormat* format, Uint8* r, Uint8* g, Uint8* b)
    void SDL_GetRGBA(Uint32 pixel, const SDL_PixelFormat* format, Uint8* r, Uint8* g, Uint8* b, Uint8* a)
    void SDL_CalculateGammaRamp(float gamma, Uint16* ramp)

cdef extern from "SDL_blendmode.h" nogil:

    ctypedef enum SDL_BlendMode:
        SDL_BLENDMODE_NONE
        SDL_BLENDMODE_BLEND
        SDL_BLENDMODE_ADD
        SDL_BLENDMODE_MOD

cdef extern from "SDL_surface.h" nogil:

    ctypedef struct SDL_BlitMap:
        pass

    ctypedef struct SDL_Surface:
        Uint32 flags
        SDL_PixelFormat* format
        int w, h
        int pitch
        void* pixels
        void* userdata
        int locked
        void* lock_data
        SDL_Rect clip_rect
        SDL_BlitMap* map
        int refcount

    ctypedef int (*SDL_blit) (SDL_Surface* src, SDL_Rect* srcrect, SDL_Surface* dst, SDL_Rect* dstrect)

    SDL_Surface* SDL_CreateRGBSurface (Uint32 flags, int width, int height, int depth, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask)
    SDL_Surface* SDL_CreateRGBSurfaceFrom(void* pixels, int width, int height, int depth, int pitch, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask)
    void SDL_FreeSurface(SDL_Surface* surface)
    int SDL_SetSurfacePalette(SDL_Surface* surface, SDL_Palette* palette)
    int SDL_LockSurface(SDL_Surface* surface)
    void SDL_UnlockSurface(SDL_Surface* surface)
    SDL_Surface* SDL_LoadBMP_RW(SDL_RWops* src, int freesrc)
    SDL_Surface* SDL_LoadBMP(char* file) # macro
    int SDL_SaveBMP_RW(SDL_Surface* surface, SDL_RWops* dst, int freedst)
    int SDL_SaveBMP(SDL_Surface* surface, const char* file) # macro
    int SDL_SetSurfaceRLE(SDL_Surface* surface, int flag)
    int SDL_SetColorKey(SDL_Surface* surface, int flag, Uint32 key)
    int SDL_GetColorKey(SDL_Surface* surface, Uint32* key)
    int SDL_SetSurfaceColorMod(SDL_Surface* surface, Uint8 r, Uint8 g, Uint8 b)
    int SDL_GetSurfaceColorMod(SDL_Surface* surface, Uint8* r, Uint8* g, Uint8* b)
    int SDL_SetSurfaceAlphaMod(SDL_Surface* surface, Uint8 alpha)
    int SDL_GetSurfaceAlphaMod(SDL_Surface* surface, Uint8* alpha)
    int SDL_SetSurfaceBlendMode(SDL_Surface* surface, SDL_BlendMode blendMode)
    int SDL_GetSurfaceBlendMode(SDL_Surface* surface, SDL_BlendMode* blendMode)
    SDL_bool SDL_SetClipRect(SDL_Surface* surface, const SDL_Rect* rect)
    void SDL_GetClipRect(SDL_Surface* surface, SDL_Rect* rect)
    SDL_Surface* SDL_ConvertSurface (SDL_Surface* src, const SDL_PixelFormat* fmt, Uint32 flags)
    SDL_Surface* SDL_ConvertSurfaceFormat (SDL_Surface* src, Uint32 pixel_format, Uint32 flags)
    int SDL_ConvertPixels(int width, int height, Uint32 src_format, const void* src, int src_pitch, Uint32 dst_format, void* dst, int dst_pitch)
    int SDL_FillRect(SDL_Surface* dst, const SDL_Rect* rect, Uint32 color)
    int SDL_FillRects(SDL_Surface* dst, const SDL_Rect* rects, int count, Uint32 color)
    int SDL_BlitSurface(SDL_Surface* src, const SDL_Rect* srcrect, SDL_Surface* dst, SDL_Rect* dstrect) # macro
    int SDL_UpperBlit(SDL_Surface* src, const SDL_Rect* srcrect, SDL_Surface* dst, SDL_Rect* dstrect)
    int SDL_LowerBlit(SDL_Surface* src, SDL_Rect* srcrect, SDL_Surface* dst, SDL_Rect* dstrect)
    int SDL_SoftStretch(SDL_Surface* src, const SDL_Rect* srcrect, SDL_Surface* dst, const SDL_Rect* dstrect)
    int SDL_UpperBlitScaled(SDL_Surface* src, const SDL_Rect* srcrect, SDL_Surface* dst, SDL_Rect* dstrect)
    int SDL_LowerBlitScaled(SDL_Surface* src, SDL_Rect* srcrect, SDL_Surface* dst, SDL_Rect* dstrect)
    int SDL_BlitScaled(SDL_Surface* src, const SDL_Rect* srcrect, SDL_Surface* dst, SDL_Rect* dstrect) # macro

cdef extern from "SDL_video.h" nogil:

    ctypedef struct SDL_DisplayMode:
        Uint32 format
        int w
        int h
        int refresh_rate
        void* driverdata

    ctypedef struct SDL_Window:
        pass

    ctypedef enum SDL_WindowFlags:
        SDL_WINDOW_FULLSCREEN
        SDL_WINDOW_OPENGL
        SDL_WINDOW_SHOWN
        SDL_WINDOW_HIDDEN
        SDL_WINDOW_BORDERLESS
        SDL_WINDOW_RESIZABLE
        SDL_WINDOW_MINIMIZED
        SDL_WINDOW_MAXIMIZED
        SDL_WINDOW_INPUT_GRABBED
        SDL_WINDOW_INPUT_FOCUS
        SDL_WINDOW_MOUSE_FOCUS
        SDL_WINDOW_FULLSCREEN_DESKTOP
        SDL_WINDOW_FOREIGN
        SDL_WINDOW_ALLOW_HIGHDPI

    ctypedef enum SDL_WindowEventID:
        SDL_WINDOWEVENT_NONE
        SDL_WINDOWEVENT_SHOWN
        SDL_WINDOWEVENT_HIDDEN
        SDL_WINDOWEVENT_EXPOSED
        SDL_WINDOWEVENT_MOVED
        SDL_WINDOWEVENT_RESIZED
        SDL_WINDOWEVENT_SIZE_CHANGED
        SDL_WINDOWEVENT_MINIMIZED
        SDL_WINDOWEVENT_MAXIMIZED
        SDL_WINDOWEVENT_RESTORED
        SDL_WINDOWEVENT_ENTER
        SDL_WINDOWEVENT_LEAVE
        SDL_WINDOWEVENT_FOCUS_GAINED
        SDL_WINDOWEVENT_FOCUS_LOST
        SDL_WINDOWEVENT_CLOSE

    ctypedef void* SDL_GLContext

    ctypedef enum SDL_GLattr:
        SDL_GL_RED_SIZE
        SDL_GL_GREEN_SIZE
        SDL_GL_BLUE_SIZE
        SDL_GL_ALPHA_SIZE
        SDL_GL_BUFFER_SIZE
        SDL_GL_DOUBLEBUFFER
        SDL_GL_DEPTH_SIZE
        SDL_GL_STENCIL_SIZE
        SDL_GL_ACCUM_RED_SIZE
        SDL_GL_ACCUM_GREEN_SIZE
        SDL_GL_ACCUM_BLUE_SIZE
        SDL_GL_ACCUM_ALPHA_SIZE
        SDL_GL_STEREO
        SDL_GL_MULTISAMPLEBUFFERS
        SDL_GL_MULTISAMPLESAMPLES
        SDL_GL_ACCELERATED_VISUAL
        SDL_GL_RETAINED_BACKING
        SDL_GL_CONTEXT_MAJOR_VERSION
        SDL_GL_CONTEXT_MINOR_VERSION
        SDL_GL_CONTEXT_EGL
        SDL_GL_CONTEXT_FLAGS
        SDL_GL_CONTEXT_PROFILE_MASK
        SDL_GL_SHARE_WITH_CURRENT_CONTEXT
        SDL_GL_FRAMEBUFFER_SRGB_CAPABLE

    ctypedef enum SDL_GLprofile:
        SDL_GL_CONTEXT_PROFILE_CORE
        SDL_GL_CONTEXT_PROFILE_COMPATIBILITY
        SDL_GL_CONTEXT_PROFILE_ES

    ctypedef enum SDL_GLcontextFlag:
        SDL_GL_CONTEXT_DEBUG_FLAG
        SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG
        SDL_GL_CONTEXT_ROBUST_ACCESS_FLAG
        SDL_GL_CONTEXT_RESET_ISOLATION_FLAG

    int SDL_WINDOWPOS_UNDEFINED # macro
    int SDL_WINDOWPOS_CENTERED # macro

    int SDL_GetNumVideoDrivers()
    const char* SDL_GetVideoDriver(int index)
    int SDL_VideoInit(const char* driver_name)
    void SDL_VideoQuit()
    const char* SDL_GetCurrentVideoDriver()
    int SDL_GetNumVideoDisplays()
    const char*  SDL_GetDisplayName(int displayIndex)
    int SDL_GetDisplayBounds(int displayIndex, SDL_Rect* rect)
    int SDL_GetNumDisplayModes(int displayIndex)
    int SDL_GetDisplayMode(int displayIndex, int modeIndex, SDL_DisplayMode* mode)
    int SDL_GetDesktopDisplayMode(int displayIndex, SDL_DisplayMode* mode)
    int SDL_GetCurrentDisplayMode(int displayIndex, SDL_DisplayMode* mode)
    SDL_DisplayMode* SDL_GetClosestDisplayMode(int displayIndex, const SDL_DisplayMode* mode, SDL_DisplayMode* closest)
    int SDL_GetWindowDisplayIndex(SDL_Window* window)
    int SDL_SetWindowDisplayMode(SDL_Window* window, const SDL_DisplayMode* mode)
    int SDL_GetWindowDisplayMode(SDL_Window* window, SDL_DisplayMode* mode)
    Uint32 SDL_GetWindowPixelFormat(SDL_Window* window)
    SDL_Window* SDL_CreateWindow(const char* title, int x, int y, int w, int h, Uint32 flags)
    SDL_Window* SDL_CreateWindowFrom(const void* data)
    Uint32 SDL_GetWindowID(SDL_Window* window)
    SDL_Window* SDL_GetWindowFromID(Uint32 id)
    Uint32 SDL_GetWindowFlags(SDL_Window* window)
    void SDL_SetWindowTitle(SDL_Window* window, const char* title)
    const char* SDL_GetWindowTitle(SDL_Window* window)
    void SDL_SetWindowIcon(SDL_Window* window, SDL_Surface* icon)
    void* SDL_SetWindowData(SDL_Window* window, const char* name, void* userdata)
    void* SDL_GetWindowData(SDL_Window* window, const char* name)
    void SDL_SetWindowPosition(SDL_Window* window, int x, int y)
    void SDL_GetWindowPosition(SDL_Window* window, int* x, int* y)
    void SDL_SetWindowSize(SDL_Window* window, int w, int h)
    void SDL_GetWindowSize(SDL_Window* window, int* w, int* h)
    void SDL_SetWindowMinimumSize(SDL_Window* window, int min_w, int min_h)
    void SDL_GetWindowMinimumSize(SDL_Window* window, int* w, int* h)
    void SDL_SetWindowMaximumSize(SDL_Window* window, int max_w, int max_h)
    void SDL_GetWindowMaximumSize(SDL_Window* window, int* w, int* h)
    void SDL_SetWindowBordered(SDL_Window* window, SDL_bool bordered)
    void SDL_ShowWindow(SDL_Window* window)
    void SDL_HideWindow(SDL_Window* window)
    void SDL_RaiseWindow(SDL_Window* window)
    void SDL_MaximizeWindow(SDL_Window* window)
    void SDL_MinimizeWindow(SDL_Window* window)
    void SDL_RestoreWindow(SDL_Window* window)
    int SDL_SetWindowFullscreen(SDL_Window* window, Uint32 flags)
    SDL_Surface* SDL_GetWindowSurface(SDL_Window* window)
    int SDL_UpdateWindowSurface(SDL_Window* window)
    int SDL_UpdateWindowSurfaceRects(SDL_Window* window, const SDL_Rect* rects, int numrects)
    void SDL_SetWindowGrab(SDL_Window* window, SDL_bool grabbed)
    SDL_bool SDL_GetWindowGrab(SDL_Window* window)
    int SDL_SetWindowBrightness(SDL_Window* window, float brightness)
    float SDL_GetWindowBrightness(SDL_Window* window)
    int SDL_SetWindowGammaRamp(SDL_Window* window, const Uint16* red, const Uint16* green, const Uint16* blue)
    int SDL_GetWindowGammaRamp(SDL_Window* window, Uint16* red, Uint16* green, Uint16* blue)
    void SDL_DestroyWindow(SDL_Window* window)
    SDL_bool SDL_IsScreenSaverEnabled()
    void SDL_EnableScreenSaver()
    void SDL_DisableScreenSaver()
    int SDL_GL_LoadLibrary(const char* path)
    void* SDL_GL_GetProcAddress(const char* proc)
    void SDL_GL_UnloadLibrary()
    SDL_bool SDL_GL_ExtensionSupported(const char* extension)
    void SDL_GL_ResetAttributes()
    int SDL_GL_SetAttribute(SDL_GLattr attr, int value)
    int SDL_GL_GetAttribute(SDL_GLattr attr, int* value)
    SDL_GLContext SDL_GL_CreateContext(SDL_Window* window)
    int SDL_GL_MakeCurrent(SDL_Window* window, SDL_GLContext context)
    SDL_Window* SDL_GL_GetCurrentWindow()
    SDL_GLContext SDL_GL_GetCurrentContext()
    void SDL_GL_GetDrawableSize(SDL_Window* window, int* w, int* h)
    int SDL_GL_SetSwapInterval(int interval)
    int SDL_GL_GetSwapInterval()
    void SDL_GL_SwapWindow(SDL_Window* window)
    void SDL_GL_DeleteContext(SDL_GLContext context)

cdef extern from "SDL_render.h" nogil:

    ctypedef Uint32 int

    ctypedef enum SDL_RendererFlags:
        SDL_RENDERER_SOFTWARE
        SDL_RENDERER_ACCELERATED
        SDL_RENDERER_PRESENTVSYNC
        SDL_RENDERER_TARGETTEXTURE

    ctypedef struct SDL_RendererInfo:
        char*  name
        Uint32 flags
        Uint32 num_texture_formats
        Uint32 texture_formats[16]
        int    max_texture_width
        int    max_texture_height

    ctypedef enum SDL_TextureAccess:
        SDL_TEXTUREACCESS_STATIC
        SDL_TEXTUREACCESS_STREAMING
        SDL_TEXTUREACCESS_TARGET

    ctypedef enum SDL_TextureModulate:
        SDL_TEXTUREMODULATE_NONE
        SDL_TEXTUREMODULATE_COLOR
        SDL_TEXTUREMODULATE_ALPHA

    ctypedef enum SDL_RendererFlip:
        SDL_FLIP_NONE
        SDL_FLIP_HORIZONTAL
        SDL_FLIP_VERTICAL

    ctypedef struct SDL_Renderer:
        pass

    ctypedef struct SDL_Texture:
        pass

    int SDL_GetNumRenderDrivers()
    int SDL_GetRenderDriverInfo(int index, SDL_RendererInfo* info)
    int SDL_CreateWindowAndRenderer(int width, int height, Uint32 window_flags, SDL_Window** window, SDL_Renderer** renderer)
    SDL_Renderer* SDL_CreateRenderer(SDL_Window* window, int index, Uint32 flags)
    SDL_Renderer* SDL_CreateSoftwareRenderer(SDL_Surface* surface)
    SDL_Renderer* SDL_GetRenderer(SDL_Window* window)
    int SDL_GetRendererInfo(SDL_Renderer* renderer, SDL_RendererInfo* info)
    int SDL_GetRendererOutputSize(SDL_Renderer* renderer, int* w, int* h)
    SDL_Texture*  SDL_CreateTexture(SDL_Renderer* renderer, Uint32 format, int access, int w, int h)
    SDL_Texture*  SDL_CreateTextureFromSurface(SDL_Renderer* renderer, SDL_Surface* surface)
    int SDL_QueryTexture(SDL_Texture* texture, Uint32* format, int* access, int* w, int* h)
    int SDL_SetTextureColorMod(SDL_Texture* texture, Uint8 r, Uint8 g, Uint8 b)
    int SDL_GetTextureColorMod(SDL_Texture* texture, Uint8* r, Uint8* g, Uint8* b)
    int SDL_SetTextureAlphaMod(SDL_Texture* texture, Uint8 alpha)
    int SDL_GetTextureAlphaMod(SDL_Texture* texture, Uint8* alpha)
    int SDL_SetTextureBlendMode(SDL_Texture* texture, SDL_BlendMode blendMode)
    int SDL_GetTextureBlendMode(SDL_Texture* texture, SDL_BlendMode* blendMode)
    int SDL_UpdateTexture(SDL_Texture* texture, const SDL_Rect* rect, const void* pixels, int pitch)
    int SDL_UpdateYUVTexture(SDL_Texture* texture, const SDL_Rect* rect, const Uint8* Yplane, int Ypitch, const Uint8* Uplane, int Upitch, const Uint8* Vplane, int Vpitch)
    int SDL_LockTexture(SDL_Texture* texture, const SDL_Rect* rect, void** pixels, int* pitch)
    void SDL_UnlockTexture(SDL_Texture* texture)
    SDL_bool SDL_RenderTargetSupported(SDL_Renderer* renderer)
    int SDL_SetRenderTarget(SDL_Renderer* renderer, SDL_Texture* texture)
    SDL_Texture* SDL_GetRenderTarget(SDL_Renderer* renderer)
    int SDL_RenderSetLogicalSize(SDL_Renderer* renderer, int w, int h)
    void SDL_RenderGetLogicalSize(SDL_Renderer* renderer, int* w, int* h)
    int SDL_RenderSetViewport(SDL_Renderer* renderer, const SDL_Rect* rect)
    void SDL_RenderGetViewport(SDL_Renderer* renderer, SDL_Rect* rect)
    int SDL_RenderSetClipRect(SDL_Renderer* renderer, const SDL_Rect* rect)
    void SDL_RenderGetClipRect(SDL_Renderer* renderer, SDL_Rect* rect)
    int SDL_RenderSetScale(SDL_Renderer* renderer, float scaleX, float scaleY)
    void SDL_RenderGetScale(SDL_Renderer* renderer, float* scaleX, float* scaleY)
    int SDL_SetRenderDrawColor(SDL_Renderer* renderer, Uint8 r, Uint8 g, Uint8 b, Uint8 a)
    int SDL_GetRenderDrawColor(SDL_Renderer* renderer, Uint8* r, Uint8* g, Uint8* b, Uint8* a)
    int SDL_SetRenderDrawBlendMode(SDL_Renderer* renderer, SDL_BlendMode blendMode)
    int SDL_GetRenderDrawBlendMode(SDL_Renderer* renderer, SDL_BlendMode* blendMode)
    int SDL_RenderClear(SDL_Renderer* renderer)
    int SDL_RenderDrawPoint(SDL_Renderer* renderer, int x, int y)
    int SDL_RenderDrawPoints(SDL_Renderer* renderer, const SDL_Point* points, int count)
    int SDL_RenderDrawLine(SDL_Renderer* renderer, int x1, int y1, int x2, int y2)
    int SDL_RenderDrawLines(SDL_Renderer* renderer, const SDL_Point* points, int count)
    int SDL_RenderDrawRect(SDL_Renderer* renderer, const SDL_Rect* rect)
    int SDL_RenderDrawRects(SDL_Renderer* renderer, const SDL_Rect* rects, int count)
    int SDL_RenderFillRect(SDL_Renderer* renderer, const SDL_Rect* rect)
    int SDL_RenderFillRects(SDL_Renderer* renderer, const SDL_Rect* rects, int count)
    int SDL_RenderCopy(SDL_Renderer* renderer, SDL_Texture* texture, const SDL_Rect* srcrect, const SDL_Rect* dstrect)
    int SDL_RenderCopyEx(SDL_Renderer* renderer, SDL_Texture* texture, const SDL_Rect* srcrect, const SDL_Rect* dstrect, const double angle, const SDL_Point* center, const SDL_RendererFlip flip)
    int SDL_RenderReadPixels(SDL_Renderer* renderer, const SDL_Rect* rect, Uint32 format, void* pixels, int pitch)
    void SDL_RenderPresent(SDL_Renderer* renderer)
    void SDL_DestroyTexture(SDL_Texture* texture)
    void SDL_DestroyRenderer(SDL_Renderer* renderer)
    int SDL_GL_BindTexture(SDL_Texture* texture, float* texw, float* texh)
    int SDL_GL_UnbindTexture(SDL_Texture* texture)

cdef extern from "SDL_audio.h" nogil:

    ctypedef Uint16 SDL_AudioFormat

    int SDL_AUDIO_MASK_BITSIZE # macro
    int SDL_AUDIO_MASK_DATATYPE # macro
    int SDL_AUDIO_MASK_ENDIAN # macro
    int SDL_AUDIO_MASK_SIGNED # macro
    int SDL_AUDIO_BITSIZE(int x) # macro
    int SDL_AUDIO_ISFLOAT(int x) # macro
    int SDL_AUDIO_ISBIGENDIAN(int x) # macro
    int SDL_AUDIO_ISSIGNED(int x) # macro
    int SDL_AUDIO_ISINT(int x) # macro
    int SDL_AUDIO_ISLITTLEENDIAN(int x) # macro
    int SDL_AUDIO_ISUNSIGNED(int x) # macro
    int AUDIO_U8 # macro
    int AUDIO_S8 # macro
    int AUDIO_U16LSB # macro
    int AUDIO_S16LSB # macro
    int AUDIO_U16MSB # macro
    int AUDIO_S16MSB # macro
    int AUDIO_U16 # macro
    int AUDIO_S16 # macro
    int AUDIO_S32LSB # macro
    int AUDIO_S32MSB # macro
    int AUDIO_S32 # macro
    int AUDIO_F32LSB # macro
    int AUDIO_F32MSB # macro
    int AUDIO_F32 # macro
    int AUDIO_U16SYS # macro
    int AUDIO_S16SYS # macro
    int AUDIO_S32SYS # macro
    int AUDIO_F32SYS # macro
    int SDL_AUDIO_ALLOW_FREQUENCY_CHANGE # macro
    int SDL_AUDIO_ALLOW_FORMAT_CHANGE # macro
    int SDL_AUDIO_ALLOW_CHANNELS_CHANGE # macro
    int SDL_AUDIO_ALLOW_ANY_CHANGE # macro

    ctypedef void (*SDL_AudioCallback) (void* userdata, Uint8* stream, int len)

    ctypedef struct SDL_AudioSpec:
        int freq
        SDL_AudioFormat format
        Uint8 channels
        Uint8 silence
        Uint16 samples
        Uint16 padding
        Uint32 size
        SDL_AudioCallback callback
        void *userdata

    ctypedef struct SDL_AudioCVT:
        pass

    ctypedef void (*SDL_AudioFilter) (SDL_AudioCVT* cvt, SDL_AudioFormat format)

    ctypedef struct SDL_AudioCVT:
        int needed
        SDL_AudioFormat src_format
        SDL_AudioFormat dst_format
        double rate_incr
        Uint8 *buf
        int len
        int len_cvt
        int len_mult
        double len_ratio
        SDL_AudioFilter filters[10]
        int filter_index


    int  SDL_GetNumAudioDrivers()
    const char* SDL_GetAudioDriver(int index)
    int SDL_AudioInit(const char* driver_name)
    void SDL_AudioQuit()
    const char * SDL_GetCurrentAudioDriver()
    int  SDL_OpenAudio(SDL_AudioSpec* desired, SDL_AudioSpec* obtained)

    ctypedef Uint32 SDL_AudioDeviceID

    int SDL_GetNumAudioDevices(int iscapture)
    const char* SDL_GetAudioDeviceName(int index, int iscapture)
    SDL_AudioDeviceID SDL_OpenAudioDevice(const char* device, int iscapture, const SDL_AudioSpec* desired, SDL_AudioSpec* obtained, int allowed_changes)

    ctypedef enum SDL_AudioStatus:
        SDL_AUDIO_STOPPED
        SDL_AUDIO_PLAYING
        SDL_AUDIO_PAUSED

    SDL_AudioStatus SDL_GetAudioStatus()
    SDL_AudioStatus SDL_GetAudioDeviceStatus(SDL_AudioDeviceID dev)
    void SDL_PauseAudio(int pause_on)
    void SDL_PauseAudioDevice(SDL_AudioDeviceID dev, int pause_on)
    SDL_AudioSpec* SDL_LoadWAV_RW(SDL_RWops* src, int freesrc, SDL_AudioSpec* spec, Uint8** audio_buf, Uint32* audio_len)
    SDL_AudioSpec* SDL_LoadWAV(const char* file, SDL_AudioSpec* spec, Uint8** audio_buf, Uint32* audio_len) # macro
    void SDL_FreeWAV(Uint8* audio_buf)
    int SDL_BuildAudioCVT(SDL_AudioCVT* cvt, SDL_AudioFormat src_format, Uint8 src_channels, int src_rate, SDL_AudioFormat dst_format, Uint8 dst_channels, int dst_rate)
    int SDL_ConvertAudio(SDL_AudioCVT* cvt)

    int SDL_MIX_MAXVOLUME # macro

    void SDL_MixAudio(Uint8* dst, const Uint8* src, Uint32 len, int volume)
    void SDL_MixAudioFormat(Uint8* dst, const Uint8* src, SDL_AudioFormat format, Uint32 len, int volume)
    void SDL_LockAudio()
    void SDL_LockAudioDevice(SDL_AudioDeviceID dev)
    void SDL_UnlockAudio()
    void SDL_UnlockAudioDevice(SDL_AudioDeviceID dev)
    void SDL_CloseAudio()
    void SDL_CloseAudioDevice(SDL_AudioDeviceID dev)

cdef extern from "SDL_scancode.h" nogil:

    ctypedef enum SDL_Scancode:
        SDL_SCANCODE_UNKNOWN

        SDL_SCANCODE_A
        SDL_SCANCODE_B
        SDL_SCANCODE_C
        SDL_SCANCODE_D
        SDL_SCANCODE_E
        SDL_SCANCODE_F
        SDL_SCANCODE_G
        SDL_SCANCODE_H
        SDL_SCANCODE_I
        SDL_SCANCODE_J
        SDL_SCANCODE_K
        SDL_SCANCODE_L
        SDL_SCANCODE_M
        SDL_SCANCODE_N
        SDL_SCANCODE_O
        SDL_SCANCODE_P
        SDL_SCANCODE_Q
        SDL_SCANCODE_R
        SDL_SCANCODE_S
        SDL_SCANCODE_T
        SDL_SCANCODE_U
        SDL_SCANCODE_V
        SDL_SCANCODE_W
        SDL_SCANCODE_X
        SDL_SCANCODE_Y
        SDL_SCANCODE_Z

        SDL_SCANCODE_1
        SDL_SCANCODE_2
        SDL_SCANCODE_3
        SDL_SCANCODE_4
        SDL_SCANCODE_5
        SDL_SCANCODE_6
        SDL_SCANCODE_7
        SDL_SCANCODE_8
        SDL_SCANCODE_9
        SDL_SCANCODE_0

        SDL_SCANCODE_RETURN
        SDL_SCANCODE_ESCAPE
        SDL_SCANCODE_BACKSPACE
        SDL_SCANCODE_TAB
        SDL_SCANCODE_SPACE

        SDL_SCANCODE_MINUS
        SDL_SCANCODE_EQUALS
        SDL_SCANCODE_LEFTBRACKET
        SDL_SCANCODE_RIGHTBRACKET
        SDL_SCANCODE_BACKSLASH
        SDL_SCANCODE_NONUSHASH
        SDL_SCANCODE_SEMICOLON
        SDL_SCANCODE_APOSTROPHE
        SDL_SCANCODE_GRAVE
        SDL_SCANCODE_COMMA
        SDL_SCANCODE_PERIOD
        SDL_SCANCODE_SLASH

        SDL_SCANCODE_CAPSLOCK

        SDL_SCANCODE_F1
        SDL_SCANCODE_F2
        SDL_SCANCODE_F3
        SDL_SCANCODE_F4
        SDL_SCANCODE_F5
        SDL_SCANCODE_F6
        SDL_SCANCODE_F7
        SDL_SCANCODE_F8
        SDL_SCANCODE_F9
        SDL_SCANCODE_F10
        SDL_SCANCODE_F11
        SDL_SCANCODE_F12

        SDL_SCANCODE_PRINTSCREEN
        SDL_SCANCODE_SCROLLLOCK
        SDL_SCANCODE_PAUSE
        SDL_SCANCODE_INSERT
        SDL_SCANCODE_HOME
        SDL_SCANCODE_PAGEUP
        SDL_SCANCODE_DELETE
        SDL_SCANCODE_END
        SDL_SCANCODE_PAGEDOWN
        SDL_SCANCODE_RIGH
        SDL_SCANCODE_LEFT
        SDL_SCANCODE_DOWN
        SDL_SCANCODE_UP

        SDL_SCANCODE_NUMLOCKCLEAR
        SDL_SCANCODE_KP_DIVIDE
        SDL_SCANCODE_KP_MULTIPLY
        SDL_SCANCODE_KP_MINUS
        SDL_SCANCODE_KP_PLUS
        SDL_SCANCODE_KP_ENTER
        SDL_SCANCODE_KP_1
        SDL_SCANCODE_KP_2
        SDL_SCANCODE_KP_3
        SDL_SCANCODE_KP_4
        SDL_SCANCODE_KP_5
        SDL_SCANCODE_KP_6
        SDL_SCANCODE_KP_7
        SDL_SCANCODE_KP_8
        SDL_SCANCODE_KP_9
        SDL_SCANCODE_KP_0
        SDL_SCANCODE_KP_PERIOD

        SDL_SCANCODE_NONUSBACKSLASH
        SDL_SCANCODE_APPLICATION
        SDL_SCANCODE_POWER
        SDL_SCANCODE_KP_EQUALS
        SDL_SCANCODE_F13
        SDL_SCANCODE_F14
        SDL_SCANCODE_F15
        SDL_SCANCODE_F16
        SDL_SCANCODE_F17
        SDL_SCANCODE_F18
        SDL_SCANCODE_F19
        SDL_SCANCODE_F20
        SDL_SCANCODE_F21
        SDL_SCANCODE_F22
        SDL_SCANCODE_F23
        SDL_SCANCODE_F24
        SDL_SCANCODE_EXECUTE
        SDL_SCANCODE_HELP
        SDL_SCANCODE_MENU
        SDL_SCANCODE_SELECT
        SDL_SCANCODE_STOP
        SDL_SCANCODE_AGAIN
        SDL_SCANCODE_UNDO
        SDL_SCANCODE_CUT
        SDL_SCANCODE_COPY
        SDL_SCANCODE_PASTE
        SDL_SCANCODE_FIND
        SDL_SCANCODE_MUTE
        SDL_SCANCODE_VOLUMEUP
        SDL_SCANCODE_VOLUMEDOWN
        SDL_SCANCODE_KP_COMMA
        SDL_SCANCODE_KP_EQUALSAS400

        SDL_SCANCODE_INTERNATIONAL1
        SDL_SCANCODE_INTERNATIONAL2
        SDL_SCANCODE_INTERNATIONAL3
        SDL_SCANCODE_INTERNATIONAL4
        SDL_SCANCODE_INTERNATIONAL5
        SDL_SCANCODE_INTERNATIONAL6
        SDL_SCANCODE_INTERNATIONAL7
        SDL_SCANCODE_INTERNATIONAL8
        SDL_SCANCODE_INTERNATIONAL9
        SDL_SCANCODE_LANG1
        SDL_SCANCODE_LANG2
        SDL_SCANCODE_LANG3
        SDL_SCANCODE_LANG4
        SDL_SCANCODE_LANG5
        SDL_SCANCODE_LANG6
        SDL_SCANCODE_LANG7
        SDL_SCANCODE_LANG8
        SDL_SCANCODE_LANG9

        SDL_SCANCODE_ALTERASE
        SDL_SCANCODE_SYSREQ
        SDL_SCANCODE_CANCEL
        SDL_SCANCODE_CLEAR
        SDL_SCANCODE_PRIOR
        SDL_SCANCODE_RETURN2
        SDL_SCANCODE_SEPARATOR
        SDL_SCANCODE_OUT
        SDL_SCANCODE_OPER
        SDL_SCANCODE_CLEARAGAIN
        SDL_SCANCODE_CRSEL
        SDL_SCANCODE_EXSEL

        SDL_SCANCODE_KP_00
        SDL_SCANCODE_KP_000
        SDL_SCANCODE_THOUSANDSSEPARATOR
        SDL_SCANCODE_DECIMALSEPARATOR
        SDL_SCANCODE_CURRENCYUNIT
        SDL_SCANCODE_CURRENCYSUBUNIT
        SDL_SCANCODE_KP_LEFTPAREN
        SDL_SCANCODE_KP_RIGHTPAREN
        SDL_SCANCODE_KP_LEFTBRACE
        SDL_SCANCODE_KP_RIGHTBRACE
        SDL_SCANCODE_KP_TAB
        SDL_SCANCODE_KP_BACKSPACE
        SDL_SCANCODE_KP_A
        SDL_SCANCODE_KP_B
        SDL_SCANCODE_KP_C
        SDL_SCANCODE_KP_D
        SDL_SCANCODE_KP_E
        SDL_SCANCODE_KP_F
        SDL_SCANCODE_KP_XOR
        SDL_SCANCODE_KP_POWER
        SDL_SCANCODE_KP_PERCENT
        SDL_SCANCODE_KP_LESS
        SDL_SCANCODE_KP_GREATER
        SDL_SCANCODE_KP_AMPERSAND
        SDL_SCANCODE_KP_DBLAMPERSAND
        SDL_SCANCODE_KP_VERTICALBAR
        SDL_SCANCODE_KP_DBLVERTICALBAR
        SDL_SCANCODE_KP_COLON
        SDL_SCANCODE_KP_HASH
        SDL_SCANCODE_KP_SPACE
        SDL_SCANCODE_KP_AT
        SDL_SCANCODE_KP_EXCLAM
        SDL_SCANCODE_KP_MEMSTORE
        SDL_SCANCODE_KP_MEMRECALL
        SDL_SCANCODE_KP_MEMCLEAR
        SDL_SCANCODE_KP_MEMADD
        SDL_SCANCODE_KP_MEMSUBTRACT
        SDL_SCANCODE_KP_MEMMULTIPLY
        SDL_SCANCODE_KP_MEMDIVIDE
        SDL_SCANCODE_KP_PLUSMINUS
        SDL_SCANCODE_KP_CLEAR
        SDL_SCANCODE_KP_CLEARENTRY
        SDL_SCANCODE_KP_BINARY
        SDL_SCANCODE_KP_OCTAL
        SDL_SCANCODE_KP_DECIMAL
        SDL_SCANCODE_KP_HEXADECIMAL

        SDL_SCANCODE_LCTRL
        SDL_SCANCODE_LSHIFT
        SDL_SCANCODE_LALT
        SDL_SCANCODE_LGUI
        SDL_SCANCODE_RCTRL
        SDL_SCANCODE_RSHIFT
        SDL_SCANCODE_RALT
        SDL_SCANCODE_RGUI

        SDL_SCANCODE_MODE

        SDL_SCANCODE_AUDIONEXT
        SDL_SCANCODE_AUDIOPREV
        SDL_SCANCODE_AUDIOSTOP
        SDL_SCANCODE_AUDIOPLAY
        SDL_SCANCODE_AUDIOMUTE
        SDL_SCANCODE_MEDIASELECT
        SDL_SCANCODE_WWW
        SDL_SCANCODE_MAIL
        SDL_SCANCODE_CALCULATOR
        SDL_SCANCODE_COMPUTER
        SDL_SCANCODE_AC_SEARCH
        SDL_SCANCODE_AC_HOME
        SDL_SCANCODE_AC_BACK
        SDL_SCANCODE_AC_FORWARD
        SDL_SCANCODE_AC_STOP
        SDL_SCANCODE_AC_REFRESH
        SDL_SCANCODE_AC_BOOKMARKS

        SDL_SCANCODE_BRIGHTNESSDOWN
        SDL_SCANCODE_BRIGHTNESSUP
        SDL_SCANCODE_DISPLAYSWITCH
        SDL_SCANCODE_KBDILLUMTOGGLE
        SDL_SCANCODE_KBDILLUMDOWN
        SDL_SCANCODE_KBDILLUMUP
        SDL_SCANCODE_EJECT
        SDL_SCANCODE_SLEEP

        SDL_SCANCODE_APP1
        SDL_SCANCODE_APP2

        SDL_NUM_SCANCODES

cdef extern from "SDL_keycode.h" nogil:

    ctypedef Sint32 SDL_Keycode

    SDL_Keycode SDL_SCANCODE_TO_KEYCODE(SDL_Scancode) # macro

    ctypedef enum:
        SDLK_UNKNOWN
        SDLK_RETURN
        SDLK_ESCAPE
        SDLK_BACKSPACE
        SDLK_TAB
        SDLK_SPACE
        SDLK_EXCLAIM
        SDLK_QUOTEDBL
        SDLK_HASH
        SDLK_PERCENT
        SDLK_DOLLAR
        SDLK_AMPERSAND
        SDLK_QUOTE
        SDLK_LEFTPAREN
        SDLK_RIGHTPAREN
        SDLK_ASTERISK
        SDLK_PLUS
        SDLK_COMMA
        SDLK_MINUS
        SDLK_PERIOD
        SDLK_SLASH
        SDLK_0
        SDLK_1
        SDLK_2
        SDLK_3
        SDLK_4
        SDLK_5
        SDLK_6
        SDLK_7
        SDLK_8
        SDLK_9
        SDLK_COLON
        SDLK_SEMICOLON
        SDLK_LESS
        SDLK_EQUALS
        SDLK_GREATER
        SDLK_QUESTION
        SDLK_AT

        SDLK_LEFTBRACKET
        SDLK_BACKSLASH
        SDLK_RIGHTBRACKET
        SDLK_CARET
        SDLK_UNDERSCORE
        SDLK_BACKQUOTE
        SDLK_a
        SDLK_b
        SDLK_c
        SDLK_d
        SDLK_e
        SDLK_f
        SDLK_g
        SDLK_h
        SDLK_i
        SDLK_j
        SDLK_k
        SDLK_l
        SDLK_m
        SDLK_n
        SDLK_o
        SDLK_p
        SDLK_q
        SDLK_r
        SDLK_s
        SDLK_t
        SDLK_u
        SDLK_v
        SDLK_w
        SDLK_x
        SDLK_y
        SDLK_z

        SDLK_CAPSLOCK

        SDLK_F1
        SDLK_F2
        SDLK_F3
        SDLK_F4
        SDLK_F5
        SDLK_F6
        SDLK_F7
        SDLK_F8
        SDLK_F9
        SDLK_F10
        SDLK_F11
        SDLK_F12

        SDLK_PRINTSCREEN
        SDLK_SCROLLLOCK
        SDLK_PAUSE
        SDLK_INSERT
        SDLK_HOME
        SDLK_PAGEUP
        SDLK_DELETE
        SDLK_END
        SDLK_PAGEDOWN
        SDLK_RIGHT
        SDLK_LEFT
        SDLK_DOWN
        SDLK_UP

        SDLK_NUMLOCKCLEAR
        SDLK_KP_DIVIDE
        SDLK_KP_MULTIPLY
        SDLK_KP_MINUS
        SDLK_KP_PLUS
        SDLK_KP_ENTER
        SDLK_KP_1
        SDLK_KP_2
        SDLK_KP_3
        SDLK_KP_4
        SDLK_KP_5
        SDLK_KP_6
        SDLK_KP_7
        SDLK_KP_8
        SDLK_KP_9
        SDLK_KP_0
        SDLK_KP_PERIOD

        SDLK_APPLICATION
        SDLK_POWER
        SDLK_KP_EQUALS
        SDLK_F13
        SDLK_F14
        SDLK_F15
        SDLK_F16
        SDLK_F17
        SDLK_F18
        SDLK_F19
        SDLK_F20
        SDLK_F21
        SDLK_F22
        SDLK_F23
        SDLK_F24
        SDLK_EXECUTE
        SDLK_HELP
        SDLK_MENU
        SDLK_SELECT
        SDLK_STOP
        SDLK_AGAIN
        SDLK_UNDO
        SDLK_CUT
        SDLK_COPY
        SDLK_PASTE
        SDLK_FIND
        SDLK_MUTE
        SDLK_VOLUMEUP
        SDLK_VOLUMEDOWN
        SDLK_KP_COMMA
        SDLK_KP_EQUALSAS400

        SDLK_ALTERASE
        SDLK_SYSREQ
        SDLK_CANCEL
        SDLK_CLEAR
        SDLK_PRIOR
        SDLK_RETURN2
        SDLK_SEPARATOR
        SDLK_OUT
        SDLK_OPER
        SDLK_CLEARAGAIN
        SDLK_CRSEL
        SDLK_EXSEL

        SDLK_KP_00
        SDLK_KP_000
        SDLK_THOUSANDSSEPARATOR
        SDLK_DECIMALSEPARATOR
        SDLK_CURRENCYUNIT
        SDLK_CURRENCYSUBUNIT
        SDLK_KP_LEFTPAREN
        SDLK_KP_RIGHTPAREN
        SDLK_KP_LEFTBRACE
        SDLK_KP_RIGHTBRACE
        SDLK_KP_TAB
        SDLK_KP_BACKSPACE
        SDLK_KP_A
        SDLK_KP_B
        SDLK_KP_C
        SDLK_KP_D
        SDLK_KP_E
        SDLK_KP_F
        SDLK_KP_XOR
        SDLK_KP_POWER
        SDLK_KP_PERCENT
        SDLK_KP_LESS
        SDLK_KP_GREATER
        SDLK_KP_AMPERSAND
        SDLK_KP_DBLAMPERSAND
        SDLK_KP_VERTICALBAR
        SDLK_KP_DBLVERTICALBAR
        SDLK_KP_COLON
        SDLK_KP_HASH
        SDLK_KP_SPACE
        SDLK_KP_AT
        SDLK_KP_EXCLAM
        SDLK_KP_MEMSTORE
        SDLK_KP_MEMRECALL
        SDLK_KP_MEMCLEAR
        SDLK_KP_MEMADD
        SDLK_KP_MEMSUBTRACT
        SDLK_KP_MEMMULTIPLY
        SDLK_KP_MEMDIVIDE
        SDLK_KP_PLUSMINUS
        SDLK_KP_CLEAR
        SDLK_KP_CLEARENTRY
        SDLK_KP_BINARY
        SDLK_KP_OCTAL
        SDLK_KP_DECIMAL
        SDLK_KP_HEXADECIMAL

        SDLK_LCTRL
        SDLK_LSHIFT
        SDLK_LALT
        SDLK_LGUI
        SDLK_RCTRL
        SDLK_RSHIFT
        SDLK_RALT
        SDLK_RGUI

        SDLK_MODE

        SDLK_AUDIONEXT
        SDLK_AUDIOPREV
        SDLK_AUDIOSTOP
        SDLK_AUDIOPLAY
        SDLK_AUDIOMUTE
        SDLK_MEDIASELECT
        SDLK_WWW
        SDLK_MAIL
        SDLK_CALCULATOR
        SDLK_COMPUTER
        SDLK_AC_SEARCH
        SDLK_AC_HOME
        SDLK_AC_BACK
        SDLK_AC_FORWARD
        SDLK_AC_STOP
        SDLK_AC_REFRESH
        SDLK_AC_BOOKMARKS

        SDLK_BRIGHTNESSDOWN
        SDLK_BRIGHTNESSUP
        SDLK_DISPLAYSWITCH
        SDLK_KBDILLUMTOGGLE
        SDLK_KBDILLUMDOWN
        SDLK_KBDILLUMUP
        SDLK_EJECT
        SDLK_SLEEP

    ctypedef enum SDL_Keymod:
        KMOD_NONE
        KMOD_LSHIFT
        KMOD_RSHIFT
        KMOD_LCTRL
        KMOD_RCTRL
        KMOD_LALT
        KMOD_RALT
        KMOD_LGUI
        KMOD_RGUI
        KMOD_NUM
        KMOD_CAPS
        KMOD_MODE
        KMOD_RESERVED

    int KMOD_CTRL # macro
    int KMOD_SHIFT # macro
    int KMOD_ALT # macro
    int KMOD_GUI # macro

cdef extern from "SDL_keyboard.h" nogil:

    ctypedef struct SDL_Keysym:
        SDL_Scancode scancode
        SDL_Keycode sym
        Uint16 mod
        Uint32 unused

    SDL_Window* SDL_GetKeyboardFocus()
    const Uint8* SDL_GetKeyboardState(int* numkeys)
    SDL_Keymod SDL_GetModState()
    void SDL_SetModState(SDL_Keymod modstate)
    SDL_Keycode SDL_GetKeyFromScancode(SDL_Scancode scancode)
    SDL_Scancode SDL_GetScancodeFromKey(SDL_Keycode key)
    const char* SDL_GetScancodeName(SDL_Scancode scancode)
    SDL_Scancode SDL_GetScancodeFromName(const char* name)
    const char* SDL_GetKeyName(SDL_Keycode key)
    SDL_Keycode SDL_GetKeyFromName(const char* name)
    void SDL_StartTextInput()
    SDL_bool   SDL_IsTextInputActive()
    void SDL_StopTextInput()
    void SDL_SetTextInputRect(SDL_Rect* rect)
    SDL_bool SDL_HasScreenKeyboardSupport()
    SDL_bool SDL_IsScreenKeyboardShown(SDL_Window* window)

cdef extern from "SDL_mouse.h" nogil:

    ctypedef struct SDL_Cursor:
        pass

    ctypedef enum SDL_SystemCursor:
        SDL_SYSTEM_CURSOR_ARROW
        SDL_SYSTEM_CURSOR_IBEAM
        SDL_SYSTEM_CURSOR_WAIT
        SDL_SYSTEM_CURSOR_CROSSHAIR
        SDL_SYSTEM_CURSOR_WAITARROW
        SDL_SYSTEM_CURSOR_SIZENWSE
        SDL_SYSTEM_CURSOR_SIZENESW
        SDL_SYSTEM_CURSOR_SIZEWE
        SDL_SYSTEM_CURSOR_SIZENS
        SDL_SYSTEM_CURSOR_SIZEALL
        SDL_SYSTEM_CURSOR_NO
        SDL_SYSTEM_CURSOR_HAND
        SDL_NUM_SYSTEM_CURSORS

    SDL_Window* SDL_GetMouseFocus()
    Uint32 SDL_GetMouseState(int* x, int* y)
    Uint32 SDL_GetRelativeMouseState(int* x, int* y)
    void SDL_WarpMouseInWindow(SDL_Window* window, int x, int y)
    int SDL_SetRelativeMouseMode(SDL_bool enabled)
    SDL_bool SDL_GetRelativeMouseMode()
    SDL_Cursor* SDL_CreateCursor(const Uint8* data, const Uint8* mask, int w, int h, int hot_x, int hot_y)
    SDL_Cursor* SDL_CreateColorCursor(SDL_Surface* surface, int hot_x, int hot_y)
    SDL_Cursor* SDL_CreateSystemCursor(SDL_SystemCursor id)
    void SDL_SetCursor(SDL_Cursor* cursor)
    SDL_Cursor* SDL_GetCursor()
    SDL_Cursor* SDL_GetDefaultCursor()
    void SDL_FreeCursor(SDL_Cursor* cursor)
    int SDL_ShowCursor(int toggle)

    enum:
        SDL_BUTTON_LEFT # macro
        SDL_BUTTON_MIDDLE # macro
        SDL_BUTTON_RIGHT # macro
        SDL_BUTTON_X1 # macro
        SDL_BUTTON_X2 # macro

cdef extern from "SDL_joystick.h" nogil:

    ctypedef struct _SDL_Joystick:
        pass

    ctypedef _SDL_Joystick SDL_Joystick

    ctypedef struct SDL_JoystickGUID:
        Uint8 data[16]

    ctypedef Sint32 SDL_JoystickID

    ctypedef enum:
        SDL_HAT_CENTERED # macro
        SDL_HAT_UP # macro
        SDL_HAT_RIGHT # macro
        SDL_HAT_DOWN # macro
        SDL_HAT_LEFT # macro
        SDL_HAT_RIGHTUP # macro
        SDL_HAT_RIGHTDOWN # macro
        SDL_HAT_LEFTUP # macro
        SDL_HAT_LEFTDOWN # macro

    int SDL_NumJoysticks()
    const char* SDL_JoystickNameForIndex(int device_index)
    SDL_Joystick* SDL_JoystickOpen(int device_index)
    const char* SDL_JoystickName(SDL_Joystick* joystick)
    SDL_JoystickGUID SDL_JoystickGetDeviceGUID(int device_index)
    SDL_JoystickGUID SDL_JoystickGetGUID(SDL_Joystick* joystick)
    void SDL_JoystickGetGUIDString(SDL_JoystickGUID guid, char* pszGUID, int cbGUID)
    SDL_JoystickGUID SDL_JoystickGetGUIDFromString(const char* pchGUID)
    SDL_bool SDL_JoystickGetAttached(SDL_Joystick* joystick)
    SDL_JoystickID SDL_JoystickInstanceID(SDL_Joystick* joystick)
    int SDL_JoystickNumAxes(SDL_Joystick* joystick)
    int SDL_JoystickNumBalls(SDL_Joystick* joystick)
    int SDL_JoystickNumHats(SDL_Joystick* joystick)
    int SDL_JoystickNumButtons(SDL_Joystick* joystick)
    void SDL_JoystickUpdate()
    int SDL_JoystickEventState(int state)
    Sint16 SDL_JoystickGetAxis(SDL_Joystick* joystick, int axis)
    Uint8 SDL_JoystickGetHat(SDL_Joystick* joystick, int hat)
    int SDL_JoystickGetBall(SDL_Joystick* joystick, int ball, int* dx, int* dy)
    Uint8 SDL_JoystickGetButton(SDL_Joystick* joystick, int button)
    void SDL_JoystickClose(SDL_Joystick* joystick)

cdef extern from "SDL_gamecontroller.h" nogil:

    ctypedef struct SDL_GameController:
        pass

    ctypedef enum SDL_GameControllerBindType:
        SDL_CONTROLLER_BINDTYPE_NONE
        SDL_CONTROLLER_BINDTYPE_BUTTON
        SDL_CONTROLLER_BINDTYPE_AXIS
        SDL_CONTROLLER_BINDTYPE_HAT

    ctypedef union __value:
        int button
        int axis

    ctypedef struct __hat:
        int hat
        int hat_mask

    ctypedef struct SDL_GameControllerButtonBind:
        SDL_GameControllerBindType bindType
        __value value
        __hat hat

    int SDL_GameControllerAddMappingsFromRW(SDL_RWops* rw, int freerw)
    int SDL_GameControllerAddMappingsFromFile(const char* file) # macro
    int SDL_GameControllerAddMapping(const char* mappingString)
    char* SDL_GameControllerMappingForGUID(SDL_JoystickGUID guid)
    char* SDL_GameControllerMapping(SDL_GameController* gamecontroller)
    SDL_bool SDL_IsGameController(int joystick_index)
    const char* SDL_GameControllerNameForIndex(int joystick_index)
    SDL_GameController* SDL_GameControllerOpen(int joystick_index)
    const char* SDL_GameControllerName(SDL_GameController* gamecontroller)
    SDL_bool SDL_GameControllerGetAttached(SDL_GameController* gamecontroller)
    SDL_Joystick* SDL_GameControllerGetJoystick(SDL_GameController* gamecontroller)
    int SDL_GameControllerEventState(int state)
    void SDL_GameControllerUpdate()

    ctypedef enum SDL_GameControllerAxis:
        SDL_CONTROLLER_AXIS_INVALID
        SDL_CONTROLLER_AXIS_LEFTX
        SDL_CONTROLLER_AXIS_LEFTY
        SDL_CONTROLLER_AXIS_RIGHTX
        SDL_CONTROLLER_AXIS_RIGHTY
        SDL_CONTROLLER_AXIS_TRIGGERLEFT
        SDL_CONTROLLER_AXIS_TRIGGERRIGHT
        SDL_CONTROLLER_AXIS_MAX

    SDL_GameControllerAxis SDL_GameControllerGetAxisFromString(const char* pchString)
    const char* SDL_GameControllerGetStringForAxis(SDL_GameControllerAxis axis)
    SDL_GameControllerButtonBind SDL_GameControllerGetBindForAxis(SDL_GameController* gamecontroller, SDL_GameControllerAxis axis)
    Sint16 SDL_GameControllerGetAxis(SDL_GameController* gamecontroller, SDL_GameControllerAxis axis)

    ctypedef enum SDL_GameControllerButton:
        SDL_CONTROLLER_BUTTON_INVALID
        SDL_CONTROLLER_BUTTON_A
        SDL_CONTROLLER_BUTTON_B
        SDL_CONTROLLER_BUTTON_X
        SDL_CONTROLLER_BUTTON_Y
        SDL_CONTROLLER_BUTTON_BACK
        SDL_CONTROLLER_BUTTON_GUIDE
        SDL_CONTROLLER_BUTTON_START
        SDL_CONTROLLER_BUTTON_LEFTSTICK
        SDL_CONTROLLER_BUTTON_RIGHTSTICK
        SDL_CONTROLLER_BUTTON_LEFTSHOULDER
        SDL_CONTROLLER_BUTTON_RIGHTSHOULDER
        SDL_CONTROLLER_BUTTON_DPAD_UP
        SDL_CONTROLLER_BUTTON_DPAD_DOWN
        SDL_CONTROLLER_BUTTON_DPAD_LEFT
        SDL_CONTROLLER_BUTTON_DPAD_RIGHT
        SDL_CONTROLLER_BUTTON_MAX

    SDL_GameControllerButton SDL_GameControllerGetButtonFromString(const char* pchString)
    const char* SDL_GameControllerGetStringForButton(SDL_GameControllerButton button)
    SDL_GameControllerButtonBind SDL_GameControllerGetBindForButton(SDL_GameController* gamecontroller, SDL_GameControllerButton button)
    Uint8 SDL_GameControllerGetButton(SDL_GameController* gamecontroller, SDL_GameControllerButton button)
    void SDL_GameControllerClose(SDL_GameController* gamecontroller)

cdef extern from "SDL_touch.h" nogil:

    ctypedef Sint64 SDL_TouchID
    ctypedef Sint64 SDL_FingerID

    ctypedef enum:
        SDL_TOUCH_MOUSEID # macro

    ctypedef struct SDL_Finger:
        SDL_FingerID id
        float x
        float y
        float pressure

    int SDL_GetNumTouchDevices()
    SDL_TouchID SDL_GetTouchDevice(int index)
    int SDL_GetNumTouchFingers(SDL_TouchID touchID)
    SDL_Finger*  SDL_GetTouchFinger(SDL_TouchID touchID, int index)

cdef extern from "SDL_gesture.h" nogil:
    ctypedef Sint64 SDL_GestureID
    int SDL_RecordGesture(SDL_TouchID touchId)
    int SDL_SaveAllDollarTemplates(SDL_RWops* dst)
    int SDL_SaveDollarTemplate(SDL_GestureID gestureId,SDL_RWops* dst)
    int SDL_LoadDollarTemplates(SDL_TouchID touchId, SDL_RWops* src)

cdef extern from "SDL_events.h" nogil:

    ctypedef enum:
        SDL_RELEASED # macro
        SDL_PRESSED # macro

    ctypedef enum SDL_EventType:
        SDL_FIRSTEVENT
        SDL_QUIT
        SDL_APP_TERMINATING
        SDL_APP_LOWMEMORY
        SDL_APP_WILLENTERBACKGROUND
        SDL_APP_DIDENTERBACKGROUND
        SDL_APP_WILLENTERFOREGROUND
        SDL_APP_DIDENTERFOREGROUND
        SDL_WINDOWEVENT
        SDL_SYSWMEVENT
        SDL_KEYDOWN
        SDL_KEYUP
        SDL_TEXTEDITING
        SDL_TEXTINPUT
        SDL_MOUSEMOTION
        SDL_MOUSEBUTTONDOWN
        SDL_MOUSEBUTTONUP
        SDL_MOUSEWHEEL
        SDL_JOYAXISMOTION
        SDL_JOYBALLMOTION
        SDL_JOYHATMOTION
        SDL_JOYBUTTONDOWN
        SDL_JOYBUTTONUP
        SDL_JOYDEVICEADDED
        SDL_JOYDEVICEREMOVED
        SDL_CONTROLLERAXISMOTION
        SDL_CONTROLLERBUTTONDOWN
        SDL_CONTROLLERBUTTONUP
        SDL_CONTROLLERDEVICEADDED
        SDL_CONTROLLERDEVICEREMOVED
        SDL_CONTROLLERDEVICEREMAPPED
        SDL_FINGERDOWN
        SDL_FINGERUP
        SDL_FINGERMOTION
        SDL_DOLLARGESTURE
        SDL_DOLLARRECORD
        SDL_MULTIGESTURE
        SDL_CLIPBOARDUPDATE
        SDL_DROPFILE
        SDL_RENDER_TARGETS_RESET
        SDL_USEREVENT
        SDL_LASTEVENT

    ctypedef struct SDL_CommonEvent:
        Uint32 type
        Uint32 timestamp

    ctypedef struct SDL_WindowEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        Uint8 event
        Uint8 padding1
        Uint8 padding2
        Uint8 padding3
        Sint32 data1
        Sint32 data2

    ctypedef struct SDL_KeyboardEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        Uint8 state
        Uint8 repeat
        Uint8 padding2
        Uint8 padding3
        SDL_Keysym keysym

    ctypedef enum:
        SDL_TEXTEDITINGEVENT_TEXT_SIZE # macro
        SDL_TEXTINPUTEVENT_TEXT_SIZE # macro

    ctypedef struct SDL_TextEditingEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        char text[SDL_TEXTEDITINGEVENT_TEXT_SIZE]
        Sint32 start
        Sint32 length

    ctypedef struct SDL_TextInputEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        char text[SDL_TEXTINPUTEVENT_TEXT_SIZE]

    ctypedef struct SDL_MouseMotionEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        Uint32 which
        Uint32 state
        Sint32 x
        Sint32 y
        Sint32 xrel
        Sint32 yrel

    ctypedef struct SDL_MouseButtonEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        Uint32 which
        Uint8 button
        Uint8 state
        Uint8 clicks
        Uint8 padding1
        Sint32 x
        Sint32 y

    ctypedef struct SDL_MouseWheelEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        Uint32 which
        Sint32 x
        Sint32 y

    ctypedef struct SDL_JoyAxisEvent:
        Uint32 type
        Uint32 timestamp
        SDL_JoystickID which
        Uint8 axis
        Uint8 padding1
        Uint8 padding2
        Uint8 padding3
        Sint16 value
        Uint16 padding4

    ctypedef struct SDL_JoyBallEvent:
        Uint32 type
        Uint32 timestamp
        SDL_JoystickID which
        Uint8 ball
        Uint8 padding1
        Uint8 padding2
        Uint8 padding3
        Sint16 xrel
        Sint16 yrel

    ctypedef struct SDL_JoyHatEvent:
        Uint32 type
        Uint32 timestamp
        SDL_JoystickID which
        Uint8 hat
        Uint8 value
        Uint8 padding1
        Uint8 padding2

    ctypedef struct SDL_JoyButtonEvent:
        Uint32 type
        Uint32 timestamp
        SDL_JoystickID which
        Uint8 button
        Uint8 state
        Uint8 padding1
        Uint8 padding2

    ctypedef struct SDL_JoyDeviceEvent:
        Uint32 type
        Uint32 timestamp
        Sint32 which

    ctypedef struct SDL_ControllerAxisEvent:
        Uint32 type
        Uint32 timestamp
        SDL_JoystickID which
        Uint8 axis
        Uint8 padding1
        Uint8 padding2
        Uint8 padding3
        Sint16 value
        Uint16 padding4

    ctypedef struct SDL_ControllerButtonEvent:
        Uint32 type
        Uint32 timestamp
        SDL_JoystickID which
        Uint8 button
        Uint8 state
        Uint8 padding1
        Uint8 padding2

    ctypedef struct SDL_ControllerDeviceEvent:
        Uint32 type
        Uint32 timestamp
        Sint32 which

    ctypedef struct SDL_TouchFingerEvent:
        Uint32 type
        Uint32 timestamp
        SDL_TouchID touchId
        SDL_FingerID fingerId
        float x
        float y
        float dx
        float dy
        float pressure

    ctypedef struct SDL_MultiGestureEvent:
        Uint32 type
        Uint32 timestamp
        SDL_TouchID touchId
        float dTheta
        float dDist
        float x
        float y
        Uint16 numFingers
        Uint16 padding

    ctypedef struct SDL_DollarGestureEvent:
        Uint32 type
        Uint32 timestamp
        SDL_TouchID touchId
        SDL_GestureID gestureId
        Uint32 numFingers
        float error
        float x
        float y

    ctypedef struct SDL_DropEvent:
        Uint32 type
        Uint32 timestamp
        char* file

    ctypedef struct SDL_QuitEvent:
        Uint32 type
        Uint32 timestamp

    ctypedef struct SDL_OSEvent:
        Uint32 type
        Uint32 timestamp

    ctypedef struct SDL_UserEvent:
        Uint32 type
        Uint32 timestamp
        Uint32 windowID
        Sint32 code
        void* data1
        void* data2

    ctypedef struct SDL_SysWMmsg:
        pass

    ctypedef struct SDL_SysWMEvent:
        Uint32 type
        Uint32 timestamp
        SDL_SysWMmsg* msg

    ctypedef union SDL_Event:
        Uint32 type
        SDL_CommonEvent common
        SDL_WindowEvent window
        SDL_KeyboardEvent key
        SDL_TextEditingEvent edit
        SDL_TextInputEvent text
        SDL_MouseMotionEvent motion
        SDL_MouseButtonEvent button
        SDL_MouseWheelEvent wheel
        SDL_JoyAxisEvent jaxis
        SDL_JoyBallEvent jball
        SDL_JoyHatEvent jhat
        SDL_JoyButtonEvent jbutton
        SDL_JoyDeviceEvent jdevice
        SDL_ControllerAxisEvent caxis
        SDL_ControllerButtonEvent cbutton
        SDL_ControllerDeviceEvent cdevice
        SDL_QuitEvent quit
        SDL_UserEvent user
        SDL_SysWMEvent syswm
        SDL_TouchFingerEvent tfinger
        SDL_MultiGestureEvent mgesture
        SDL_DollarGestureEvent dgesture
        SDL_DropEvent drop
        Uint8 padding[56]

    ctypedef enum SDL_eventaction:
        SDL_ADDEVENT
        SDL_PEEKEVENT
        SDL_GETEVENT

    ctypedef enum:
        SDL_QUERY # macro
        SDL_IGNORE # macro
        SDL_DISABLE # macro
        SDL_ENABLE # macro

    ctypedef int (*SDL_EventFilter) (void* userdata, SDL_Event* event)

    void SDL_PumpEvents()
    int SDL_PeepEvents(SDL_Event* events, int numevents, SDL_eventaction action, Uint32 minType, Uint32 maxType)
    SDL_bool SDL_HasEvent(Uint32 type)
    SDL_bool SDL_HasEvents(Uint32 minType, Uint32 maxType)
    void SDL_FlushEvent(Uint32 type)
    void SDL_FlushEvents(Uint32 minType, Uint32 maxType)
    int SDL_PollEvent(SDL_Event* event)
    int SDL_WaitEvent(SDL_Event* event)
    int SDL_WaitEventTimeout(SDL_Event* event, int timeout)
    int SDL_PushEvent(SDL_Event* event)
    void SDL_SetEventFilter(SDL_EventFilter filter, void* userdata)
    SDL_bool SDL_GetEventFilter(SDL_EventFilter* filter, void** userdata)
    void SDL_AddEventWatch(SDL_EventFilter filter, void* userdata)
    void SDL_DelEventWatch(SDL_EventFilter filter, void* userdata)
    void SDL_FilterEvents(SDL_EventFilter filter, void* userdata)
    Uint8 SDL_EventState(Uint32 type, int state)
    Uint8 SDL_GetEventState(Uint32 type) # macro
    Uint32 SDL_RegisterEvents(int numevents)

cdef extern from "SDL_hints.h" nogil:

    const char* SDL_HINT_FRAMEBUFFER_ACCELERATION # macro
    const char* SDL_HINT_RENDER_DRIVER # macro
    const char* SDL_HINT_RENDER_OPENGL_SHADERS # macro
    const char* SDL_HINT_RENDER_DIRECT3D_THREADSAFE # macro
    const char* SDL_HINT_RENDER_DIRECT3D11_DEBUG # macro
    const char* SDL_HINT_RENDER_SCALE_QUALITY # macro
    const char* SDL_HINT_RENDER_VSYNC # macro
    const char* SDL_HINT_VIDEO_ALLOW_SCREENSAVER # macro
    const char* SDL_HINT_VIDEO_X11_XVIDMODE # macro
    const char* SDL_HINT_VIDEO_X11_XINERAMA # macro
    const char* SDL_HINT_VIDEO_X11_XRANDR # macro
    const char* SDL_HINT_GRAB_KEYBOARD # macro
    const char* SDL_HINT_MOUSE_RELATIVE_MODE_WARP # macro
    const char* SDL_HINT_VIDEO_MINIMIZE_ON_FOCUS_LOSS # macro
    const char* SDL_HINT_IDLE_TIMER_DISABLED # macro
    const char* SDL_HINT_ORIENTATIONS # macro
    const char* SDL_HINT_ACCELEROMETER_AS_JOYSTICK # macro
    const char* SDL_HINT_XINPUT_ENABLED # macro
    const char* SDL_HINT_GAMECONTROLLERCONFIG # macro
    const char* SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS # macro
    const char* SDL_HINT_ALLOW_TOPMOST # macro
    const char* SDL_HINT_TIMER_RESOLUTION # macro
    const char* DL_HINT_VIDEO_HIGHDPI_DISABLED # macro
    const char* SDL_HINT_MAC_CTRL_CLICK_EMULATE_RIGHT_CLICK # macro
    const char* SDL_HINT_VIDEO_WIN_D3DCOMPILER
    const char* SDL_HINT_VIDEO_WINDOW_SHARE_PIXEL_FORMAT # macro
    const char* SDL_HINT_WINRT_PRIVACY_POLICY_URL # macro
    const char* SDL_HINT_WINRT_PRIVACY_POLICY_LABEL # macro
    const char* SDL_HINT_WINRT_HANDLE_BACK_BUTTON # macro
    const char* SDL_HINT_VIDEO_MAC_FULLSCREEN_SPACES # macro

    ctypedef enum SDL_HintPriority:
        SDL_HINT_DEFAULT
        SDL_HINT_NORMAL
        SDL_HINT_OVERRIDE

    SDL_bool SDL_SetHintWithPriority(const char* name, const char* value, SDL_HintPriority priority)
    SDL_bool SDL_SetHint(const char* name, const char *value)
    const char* SDL_GetHint(const char *name)

    ctypedef void (*SDL_HintCallback)(void* userdata, const char* name, const char* oldValue, const char* newValue)

    void SDL_AddHintCallback(const char* name, SDL_HintCallback callback, void* userdata)
    void SDL_DelHintCallback(const char* name, SDL_HintCallback callback, void *userdata)
    void SDL_ClearHints()

cdef extern from "SDL_platform.h" nogil:

    const char* SDL_GetPlatform()
