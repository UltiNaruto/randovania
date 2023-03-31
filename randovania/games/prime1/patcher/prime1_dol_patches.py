import dataclasses

import py_randomprime

from randovania.dol_patching import assembler
from randovania.dol_patching.assembler import custom_ppc
from randovania.dol_patching.assembler.ppc import addi, andis, b, beq, bgt, bl, cmpw, fcmpu, fsubs, lfs, li, lis, lwz, or_, stfs, stw, \
                                                  cr0, f1, f2, f14, r1, r3, r4, r5, r6, r7, r13, r31
from randovania.games.game import RandovaniaGame
from randovania.patching.prime.all_prime_dol_patches import BasePrimeDolVersion, StringDisplayPatchAddresses, \
    PowerupFunctionsAddresses


@dataclasses.dataclass(frozen=True)
class Prime1DolVersion(BasePrimeDolVersion):
    state_for_world: int
    set_layer_active: int

    def __init__(self, version: str, description: str, build_string_address: int,
                 build_string: bytes, sda2_base: int, sda13_base: int, cplayer_vtable: int,
                 message_receiver_string_ref: int):
        symbols = py_randomprime.symbols_for_version(version)

        super().__init__(
            game=RandovaniaGame.METROID_PRIME,
            description=description,
            build_string_address=build_string_address,
            build_string=build_string,
            sda2_base=sda2_base,
            sda13_base=sda13_base,
            game_state_pointer=symbols["g_GameState"],
            cplayer_vtable=cplayer_vtable,
            cstate_manager_global=symbols["g_StateManager"],
            string_display=StringDisplayPatchAddresses(
                update_hint_state=symbols["UpdateHintState__13CStateManagerFf"],
                message_receiver_string_ref=message_receiver_string_ref,
                wstring_constructor=symbols["wstring_l__4rstlFPCw"],
                display_hud_memo=symbols["DisplayHudMemo__9CSamusHudFRC7wstringRC12SHudMemoInfo"],
                max_message_size=200,
            ),
            powerup_functions=PowerupFunctionsAddresses(
                add_power_up=symbols["InitializePowerUp__12CPlayerStateFQ212CPlayerState9EItemTypei"],
                incr_pickup=symbols["IncrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei"],
                decr_pickup=symbols["DecrPickUp__12CPlayerStateFQ212CPlayerState9EItemTypei"],
            ),
        )
        object.__setattr__(self, "state_for_world", symbols["StateForWorld__10CGameStateFUi"])
        object.__setattr__(self, "set_layer_active", symbols["SetLayerActive__16CWorldLayerStateFiib"])
        object.__setattr__(self, "freeze", symbols["Freeze__7CPlayerFR13CStateManagerUiUsUi"])


def set_artifact_layer_active_patch(addresses: Prime1DolVersion, layer_id: int, active: bool,
                                    ) -> list[assembler.BaseInstruction]:
    # g_GameState->StateForWorld(0x39F2DE28)->GetLayerState()->SetLayerActive(templeAreaIndex, artifactLayer, true)
    result = []

    for_another_world = [
        # Get the LayerState via the CGameState
        lwz(r3, addresses.game_state_pointer - addresses.sda13_base, r13),  # get g_GameState
        # r4 already have the asset id
        bl(addresses.state_for_world),  # CGameState::StateForWorld
        lwz(r3, 0x14, r3),  # worldState->layerState
    ]

    result.extend([
        # Get the LayerState of current world. We'll overwrite if it's another world, it's just 1 instruction bigger
        lwz(r3, 0x8c8, r31),  # mgr->worldLayerState

        # Tallon Overworld asset id
        custom_ppc.load_unsigned_32bit(r4, 0x39f2de28),

        # Load current asset id in r5
        lwz(r5, 0x850, r31),  # mgr->world
        lwz(r5, 0x8, r5),  # world->mlvlId

        cmpw(0, r4, r5),  # compare asset ids
        beq(4 + assembler.byte_count(for_another_world), relative=True),
        *for_another_world,
        lwz(r3, 0x0, r3),

        # Set layer
        li(r4, 16),  # Artifact Layer
        stw(r4, 0x10, r1),

        # Set layer
        li(r5, layer_id),  # Artifact Layer
        stw(r5, 0x14, r1),

        # Make the layer change via SetLayerActive
        addi(r4, r1, 0x10),
        addi(r5, r1, 0x14),
        li(r6, int(active)),
        bl(addresses.set_layer_active),  # CWorldLayerState::SetLayerActive
    ])

    return result


def freeze_player(addresses: Prime1DolVersion) -> list[assembler.BaseInstruction]:
    return [
        lwz(r3, 0x84c, r31),  # player = manager->players[0]
        or_(r4, r31, r31),     # get mgr
        custom_ppc.load_unsigned_32bit(r5, 0x6fc03d46), # steamTextureId (0x6fc03d46)
        li(r6, 0xc34),  # sfxId = 0xc34
        custom_ppc.load_unsigned_32bit(r7, 0x2b757945),  # iceTextureId (0x2b757945)
        bl(addresses.freeze),
    ]


def damage_player(addresses: Prime1DolVersion, value: float) -> list[assembler.BaseInstruction]:
    return [
        # store current address to get static datas later
        custom_ppc.load_current_address(r4),
        # static datas
        b(0x8, relative=True),
        custom_ppc.float32(value),

        # actual function
        lfs(f1, 0xc, r4),
        lwz(r3, 0x8b8, r31),
        lwz(r3, 0, r3),
        lfs(f2, 0xc, r3),
        fsubs(f2, f2, f1),
        stfs(f2, 0xc, r3),
        fcmpu(cr0, f2, f14),
        bgt(0x10, relative=True),
        lwz(r4, 0x0, r3),
        andis(r4, r4, 0x7fff),
        stw(r4, 0x0, r3),
    ]
