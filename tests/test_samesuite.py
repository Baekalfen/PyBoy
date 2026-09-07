#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import json

import os
import numpy as np
import pytest

from pyboy import PyBoy

OVERWRITE_JSON = False

samesuite_json = "tests/test_results/samesuite.json"

HEX_DIGITS = "0123456789ABCDEF"
PASS_RESULT = '\x03\x05\x08\r\x15"'


def samesuite_result(pyboy):
    def decode_digit(tile, base):
        for offset in (0, 0x31):
            digit = tile - base - offset
            if 0 <= digit < len(HEX_DIGITS):
                return HEX_DIGITS[digit]
        return None

    rows = []
    for y in range(18):
        address = "".join(decode_digit(pyboy.tilemap_background[x, y], 0x11) or "" for x in range(4))
        values = []
        for x in range(4, 20, 2):
            high = decode_digit(pyboy.tilemap_background[x, y], 0x21)
            low = decode_digit(pyboy.tilemap_background[x + 1, y], 0x01)
            if high is None or low is None:
                values = []
                break
            values.append(high + low)

        if len(address) == 4 and values:
            rows.append(f"{address}: {' '.join(values)}")

    assert rows, "SameSuite result table not found"

    serial_result = pyboy._serial()
    if serial_result == PASS_RESULT:
        rows.append("Passed")
    elif serial_result:
        rows.append("Failed")
    return "\n".join(rows) + "\n"


SAMESUITE_ROMS = [
    "interrupt/ei_delay_halt.gb",
    "apu/div_write_trigger.gb",
    "apu/div_write_trigger_volume_10.gb",
    "apu/div_write_trigger_volume.gb",
    "apu/div_write_trigger_10.gb",
    "apu/channel_1/channel_1_freq_change_timing-cgbDE.gb",
    "apu/channel_1/channel_1_delay.gb",
    "apu/channel_1/channel_1_sweep.gb",
    "apu/channel_1/channel_1_duty.gb",
    "apu/channel_1/channel_1_nrx2_speed_change.gb",
    "apu/channel_1/channel_1_sweep_restart.gb",
    "apu/channel_1/channel_1_freq_change_timing-cgb0BC.gb",
    "apu/channel_1/channel_1_align_cpu.gb",
    "apu/channel_1/channel_1_sweep_restart_2.gb",
    "apu/channel_1/channel_1_extra_length_clocking-cgb0B.gb",
    "apu/channel_1/channel_1_restart.gb",
    "apu/channel_1/channel_1_duty_delay.gb",
    "apu/channel_1/channel_1_align.gb",
    "apu/channel_1/channel_1_freq_change_timing-A.gb",
    "apu/channel_1/channel_1_volume_div.gb",
    "apu/channel_1/channel_1_volume.gb",
    "apu/channel_1/channel_1_stop_div.gb",
    "apu/channel_1/channel_1_restart_nrx2_glitch.gb",
    "apu/channel_1/channel_1_stop_restart.gb",
    "apu/channel_1/channel_1_freq_change.gb",
    "apu/channel_1/channel_1_nrx2_glitch.gb",
    "apu/div_trigger_volume_10.gb",
    "apu/channel_3/channel_3_extra_length_clocking-cgbB.gb",
    "apu/channel_3/channel_3_freq_change_delay.gb",
    "apu/channel_3/channel_3_stop_div.gb",
    "apu/channel_3/channel_3_extra_length_clocking-cgb0.gb",
    "apu/channel_3/channel_3_restart_during_delay.gb",
    "apu/channel_3/channel_3_and_glitch.gb",
    "apu/channel_3/channel_3_restart_stop_delay.gb",
    "apu/channel_3/channel_3_wave_ram_locked_write.gb",
    "apu/channel_3/channel_3_shift_delay.gb",
    "apu/channel_3/channel_3_shift_skip_delay.gb",
    "apu/channel_3/channel_3_delay.gb",
    "apu/channel_3/channel_3_wave_ram_sync.gb",
    "apu/channel_3/channel_3_stop_delay.gb",
    "apu/channel_3/channel_3_wave_ram_dac_on_rw.gb",
    "apu/channel_3/channel_3_first_sample.gb",
    "apu/channel_3/channel_3_restart_delay.gb",
    "apu/channel_4/channel_4_lfsr_restart.gb",
    "apu/channel_4/channel_4_lfsr.gb",
    "apu/channel_4/channel_4_frequency_alignment.gb",
    "apu/channel_4/channel_4_lfsr_15_7.gb",
    "apu/channel_4/channel_4_align.gb",
    "apu/channel_4/channel_4_equivalent_frequencies.gb",
    "apu/channel_4/channel_4_volume_div.gb",
    "apu/channel_4/channel_4_lfsr15.gb",
    "apu/channel_4/channel_4_lfsr_7_15.gb",
    "apu/channel_4/channel_4_extra_length_clocking-cgb0B.gb",
    "apu/channel_4/channel_4_freq_change.gb",
    "apu/channel_4/channel_4_delay.gb",
    "apu/channel_4/channel_4_lfsr_restart_fast.gb",
    "apu/channel_2/channel_2_align.gb",
    "apu/channel_2/channel_2_duty_delay.gb",
    "apu/channel_2/channel_2_duty.gb",
    "apu/channel_2/channel_2_volume.gb",
    "apu/channel_2/channel_2_stop_restart.gb",
    "apu/channel_2/channel_2_align_cpu.gb",
    "apu/channel_2/channel_2_extra_length_clocking-cgb0B.gb",
    "apu/channel_2/channel_2_restart.gb",
    "apu/channel_2/channel_2_stop_div.gb",
    "apu/channel_2/channel_2_freq_change.gb",
    "apu/channel_2/channel_2_nrx2_glitch.gb",
    "apu/channel_2/channel_2_delay.gb",
    "apu/channel_2/channel_2_volume_div.gb",
    "apu/channel_2/channel_2_nrx2_speed_change.gb",
    "apu/channel_2/channel_2_restart_nrx2_glitch.gb",
    "dma/gdma_addr_mask.gb",
    "dma/hdma_mode0.gb",
    "dma/hdma_lcd_off.gb",
    "dma/gbc_dma_cont.gb",
    "ppu/blocking_bgpi_increase.gb",
]

# The SameSuite APU README documents that pre-CGB hardware only passes the two
# DIV-trigger tests; DMA and CGB-only PPU tests also intentionally fail on DMG.
DMG_HARDWARE_FAILURES = {
    rom
    for rom in SAMESUITE_ROMS
    if (rom.startswith("apu/") and rom not in {"apu/div_write_trigger.gb", "apu/div_write_trigger_10.gb"})
    or rom.startswith(("dma/", "ppu/"))
}


@pytest.mark.parametrize("rom", SAMESUITE_ROMS)
@pytest.mark.parametrize("cgb", [False, True], ids=["DMG", "CGB"])
def test_samesuite(rom, cgb, samesuite_dir, boot_cgb_rom, boot_rom, default_rom):
    pyboy = PyBoy(
        samesuite_dir + rom,
        window="null",
        cgb=cgb,
        bootrom=boot_cgb_rom if cgb else boot_rom,
    )
    pyboy.set_emulation_speed(0)
    pyboy.tick(180 if cgb else 350, True)

    for _ in range(10):
        if np.all(pyboy.screen.ndarray[:, :, :-1] > 240):
            pyboy.tick(20, True)
        else:
            break

    result = samesuite_result(pyboy)
    with open(samesuite_json, "r") as f:
        old_samesuite = json.load(f)

    result_key = f"{rom} [CGB]" if cgb else rom
    if OVERWRITE_JSON:
        with open(samesuite_json, "w") as f:
            old_samesuite[result_key] = result
            json.dump(old_samesuite, f, indent=4)
    else:
        expected_result = old_samesuite.get(result_key, old_samesuite[rom])
        assert result == expected_result, f"Outputs don't match for {rom}"
        if expected_result.rstrip().endswith("Failed"):
            if not cgb and rom in DMG_HARDWARE_FAILURES:
                pyboy.stop(save=False)
                return
            pyboy.stop(save=False)
            pytest.xfail(f"{rom} has a recorded failure")
        if expected_result != result and os.environ.get("TEST_VERBOSE_IMAGES"):
            pyboy.screen.image.show()

    pyboy.stop(save=False)
