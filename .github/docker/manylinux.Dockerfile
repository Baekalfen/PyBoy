ARG BASE_IMAGE=quay.io/pypa/manylinux_2_28_x86_64:latest
FROM ${BASE_IMAGE}

ARG MANYLINUX_VERSION
RUN case "${MANYLINUX_VERSION}" in \
        manylinux_*) \
            dnf install -y https://download1.rpmfusion.org/free/el/rpmfusion-free-release-8.noarch.rpm && \
            dnf install -y libjpeg-devel ccache ffmpeg && \
            dnf clean all && rm -rf /var/cache/dnf ;; \
        musllinux_*) \
            apk add libjpeg jpeg-dev libffi ccache ffmpeg && \
            rm -rf /var/cache/apk/* ;; \
        *) echo "Unsupported manylinux image: ${MANYLINUX_VERSION}" >&2; exit 1 ;; \
    esac
