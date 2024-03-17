INCLUDE "hardware.inc"

SECTION "Header", ROM0[$100]
EntryPoint:
	nop
	jp Main

SECTION "Title", ROM0[$134]
	db "DEFAULT-ROM"

SECTION "Tileset", ROM0
Tileset:
INCBIN "default_rom.2bpp"

SECTION "Tilemap", ROM0
Tilemap:
Tilemap2: ; Used to test when two symbols point to the same address
	db $40, $41, $42, $43, $44, $45, $46, $41, $41, $41, $47, $41, $41, $41
	db $48, $49, $4A, $4B, $4C, $4D, $4E, $49, $4F, $50, $51, $41, $41, $41

SECTION "CartridgeType", ROM0[$147]
	db $11

SECTION "CartridgeROMCount", ROM0[$148]
	db $00

SECTION "CartridgeRAMCount", ROM0[$149]
	db $05

SECTION "Main", ROM0[$150]
Main:
	nop
	di
	jp .setup


.waitVBlank
	ldh a, [rLY]
	cp 144
	jr c, .waitVBlank
	ret

.setup
	ld hl, rLCDC
	set 6, [hl]
	set 5, [hl]
	ld hl, rWY
	ld [hl], 144
	inc hl
	ld [hl], 43

	ld bc, $8400
	ld de, $8700
	ld hl, Tileset

.readTileset
	call .waitVBlank
	ld a, [hli]
	ld [bc], a
	inc bc
	ld a, b
	cp a, d
	jr c, .readTileset

	ld hl, Tilemap
	ld bc, $9C00
	ld de, $9C0E

.readTilemap
	call .waitVBlank
	ld a, [hli]
	ld [bc], a
	inc bc
	ld a, c
	cp a, e
	jr c, .readTilemap

	add $12
	ld c, a
	ld a, e
	add $20
	ld e, a
	ld a, e

	cp a, $2F
	jr c, .readTilemap

	ld hl, _OAMRAM

.clearOAM
	call .waitVBlank
	ld [hl], 0
	inc hl
	ld a, l
	cp a, $F0
	jr nz, .clearOAM

.loop
	ld a, [rWY]
	cp a, 90
	jr c, .loop

	ldh a, [rDIV]
	cp a, 255
	jp z, .move
	jr .loop

.sync
	ldh a, [rLY]
	cp 144
	jr nz, .sync
	ret

.move
	call .sync
	ld hl, rWY
	dec [hl]

	ldh [rDIV], a
	jr .loop
