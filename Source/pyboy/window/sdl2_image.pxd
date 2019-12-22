# Cython PXD file for SDL2_image 2.0.0
from sdl2.SDL2 cimport *

cdef extern from "SDL_image.h" nogil:

    ctypedef enum IMG_InitFlags:
        IMG_INIT_JPG
        IMG_INIT_PNG
        IMG_INIT_TIF
        IMG_INIT_WEBP

    int IMG_Init(int flags)
    void IMG_Quit()
    SDL_Surface* IMG_LoadTyped_RW(SDL_RWops* src, int freesrc, const char* type)

    SDL_Surface* IMG_Load(const char* file)
    SDL_Surface* IMG_Load_RW(SDL_RWops* src, int freesrc)
    SDL_Texture* IMG_LoadTexture(SDL_Renderer* renderer, const char* file)
    SDL_Texture* IMG_LoadTexture_RW(SDL_Renderer* renderer, SDL_RWops* src, int freesrc)
    SDL_Texture* IMG_LoadTextureTyped_RW(SDL_Renderer* renderer, SDL_RWops* src, int freesrc, const char* type)
    int IMG_isICO(SDL_RWops* src)
    int IMG_isCUR(SDL_RWops* src)
    int IMG_isBMP(SDL_RWops* src)
    int IMG_isGIF(SDL_RWops* src)
    int IMG_isJPG(SDL_RWops* src)
    int IMG_isLBM(SDL_RWops* src)
    int IMG_isPCX(SDL_RWops* src)
    int IMG_isPNG(SDL_RWops* src)
    int IMG_isPNM(SDL_RWops* src)
    int IMG_isTIF(SDL_RWops* src)
    int IMG_isXCF(SDL_RWops* src)
    int IMG_isXPM(SDL_RWops* src)
    int IMG_isXV(SDL_RWops* src)
    int IMG_isWEBP(SDL_RWops* src)
    SDL_Surface* IMG_LoadICO_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadCUR_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadBMP_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadGIF_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadJPG_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadLBM_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadPCX_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadPNG_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadPNM_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadTGA_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadTIF_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadXCF_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadXPM_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadXV_RW(SDL_RWops* src)
    SDL_Surface* IMG_LoadWEBP_RW(SDL_RWops* src)
    SDL_Surface* IMG_ReadXPMFromArray(char** xpm)
    int IMG_SavePNG(SDL_Surface* surface, const char* file)
    int IMG_SavePNG_RW(SDL_Surface* surface, SDL_RWops* dst, int freedst)
