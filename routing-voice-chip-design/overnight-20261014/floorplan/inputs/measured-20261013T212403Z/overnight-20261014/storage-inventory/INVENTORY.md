# RouteVoice storage-element inventory (merged all-on-chip RTL)

Generated 2026-10-14T02:35:43 from a Verilator 5.050 `--json-only` elaboration of `rv_allonchip_top_all_v1` (exact file list/includes of `onchip-all/commands.json` key `lint-full`). 235 parameter-specialised modules, 30,542 module instances after walking the cell tree from the top. All numbers are logical state bits from RTL declarations multiplied by instance count; they are not physical area.

## (b) Totals

| Category | Bits | Bytes |
|---|---:|---:|
| **Fixed ROM, `$readmemh` arrays (17 arrays, never written)** | 229,130,240 | **28,641,280** |
| Fixed ROM, case-statement LUT functions (pre-existing "already onboard" tables) | 70,821,044 | 8,852,630.5 |
| &nbsp;&nbsp;of which the 5 big service tables (index image, book pages, source KV index, metadata, decoder norms) | 70,778,880 | 8,847,360 |
| **ROM total** | 299,951,284 | **37,493,910.5** |
| **Mutable unpacked arrays** (written in clocked always blocks; 144 array declarations) | 8,501,818 | **1,062,727.2** |
| **Registers** (non-array variables with non-blocking writes in clocked blocks, incl. wide packed vectors) | **237,524** | 29,690.5 |
| **Mutable total (arrays + registers)** | 8,739,342 | **1,092,417.8** |
| Not counted: loop indices / blocking-only temporaries in clocked blocks | 2,368 | 296 |
| Not counted: unpacked arrays that are combinational nets (always @*/assign/cell outputs) | 360,929 | 45,116.1 |

The `$readmemh` ROM total is exactly the 28,641,280 bytes recorded in `onchip-all/rom-accounting.json` (`new_native_ROM_bytes`). The big-5 case-LUT total equals that file's `already_onboard_logical_image_bytes` (8,847,360).

## (a) Top 30 storage arrays (ROM and mutable)

| # | Hierarchical path | Module (orig) | Dims | Bits (all instances) | Bytes | Class |
|---:|---|---|---|---:|---:|---|
| 1 | `TOP.encoder_memory.rom` | `rv_onchip_encoder_memory_v1` | [160840] x 256b | 41,175,040 | 5,146,880 | ROM ($readmemh, never written) |
| 2 | `TOP.decoder_body.ff_up_coeff` | `rv_onchip_decoder_body_v1` | [153600] x 256b | 39,321,600 | 4,915,200 | ROM ($readmemh, never written) |
| 3 | `TOP.frontend_rom.conv1_weights` | `rv_onchip_frontend_v1` | [1024000] x 32b | 32,768,000 | 4,096,000 | ROM ($readmemh, never written) |
| 4 | `TOP.frontend_rom.conv2_weights` | `rv_onchip_frontend_v1` | [1024000] x 32b | 32,768,000 | 4,096,000 | ROM ($readmemh, never written) |
| 5 | `TOP.decoder_body.ff_down_coeff` | `rv_onchip_decoder_body_v1` | [76800] x 256b | 19,660,800 | 2,457,600 | ROM ($readmemh, never written) |
| 6 | `TOP.decoder_self.self_coeff` | `rv_onchip_decoder_self_v1` | [76800] x 256b | 19,660,800 | 2,457,600 | ROM ($readmemh, never written) |
| 7 | `TOP.encoder_head.rom` | `rv_onchip_encoder_head_v1` | [46080] x 320b | 14,745,600 | 1,843,200 | ROM ($readmemh, never written) |
| 8 | `TOP.positions.image` | `rv_source_position_immutable_rom_v1` | [163840] x 64b | 10,485,760 | 1,310,720 | ROM ($readmemh, never written) |
| 9 | `TOP.decoder_body.cross_coeff` | `rv_onchip_decoder_body_v1` | [38400] x 256b | 9,830,400 | 1,228,800 | ROM ($readmemh, never written) |
| 10 | `TOP.encoder_O.rom` | `rv_onchip_encoder_O_v1` | [1920] x 2560b | 4,915,200 | 614,400 | ROM ($readmemh, never written) |
| 11 | `TOP.decoder_body.ff_up_meta` | `rv_onchip_decoder_body_v1` | [7680] x 256b | 1,966,080 | 245,760 | ROM ($readmemh, never written) |
| 12 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.history_nexus.history_payload.committed` | `rv_compact_history_storage_v1` | [4356] x 256b | 1,115,136 | 139,392 | mutable (clocked write) |
| 13 | `TOP.frontend_rom.linear_weights` | `rv_onchip_frontend_v1` | [25600] x 32b | 819,200 | 102,400 | ROM ($readmemh, never written) |
| 14 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.keys` | `taalas_compact_history_layer_self_o_q1` | [21120] x 32b | 675,840 | 84,480 | mutable (clocked write) |
| 15 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.values` | `taalas_compact_history_layer_self_o_q1` | [21120] x 32b | 675,840 | 84,480 | mutable (clocked write) |
| 16 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.bridge.feature_bank` | `rv_frontend_encoder_bridge` | [20480] x 32b | 655,360 | 81,920 | mutable (clocked write) |
| 17 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.backend.banks.bank0` | `rv_encoder_bank_consumer_edge_v1` | [2560] x 256b | 655,360 | 81,920 | mutable (clocked write) |
| 18 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.backend.banks.bank1` | `rv_encoder_bank_consumer_edge_v1` | [2560] x 256b | 655,360 | 81,920 | mutable (clocked write) |
| 19 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.producer_nexus.bank.bankA` | `rv_producer_mutable_storage_v1` | [2560] x 256b | 655,360 | 81,920 | mutable (clocked write) |
| 20 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.producer_nexus.bank.bankB` | `rv_producer_mutable_storage_v1` | [2560] x 256b | 655,360 | 81,920 | mutable (clocked write) |
| 21 | `TOP.decoder_self.self_meta` | `rv_onchip_decoder_self_v1` | [1920] x 256b | 491,520 | 61,440 | ROM ($readmemh, never written) |
| 22 | `TOP.original.frontend_nexus.banks.region6` | `rv_frontend_mutable_storage_v3` | [7680] x 32b | 245,760 | 30,720 | mutable (clocked write) |
| 23 | `TOP.decoder_body.cross_meta` | `rv_onchip_decoder_body_v1` | [960] x 256b | 245,760 | 30,720 | ROM ($readmemh, never written) |
| 24 | `TOP.decoder_body.ff_down_meta` | `rv_onchip_decoder_body_v1` | [960] x 256b | 245,760 | 30,720 | ROM ($readmemh, never written) |
| 25 | `TOP.original.frontend_nexus.banks.region2` | `rv_frontend_mutable_storage_v3` | [6400] x 32b | 204,800 | 25,600 | mutable (clocked write) |
| 26 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.backend.banks.bank2` | `rv_encoder_bank_consumer_edge_v1` | [640] x 256b | 163,840 | 20,480 | mutable (clocked write) |
| 27 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.producer_nexus.bank.bankCodes` | `rv_producer_mutable_storage_v1` | [640] x 256b | 163,840 | 20,480 | mutable (clocked write) |
| 28 | `TOP.original.frontend_nexus.banks.region3` | `rv_frontend_mutable_storage_v3` | [5120] x 32b | 163,840 | 20,480 | mutable (clocked write) |
| 29 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.endpoint.projector.core.integer_path.queries[0].core.accum` (+15 more instances) | `rv_q8_generic_integer_projection_attention_v1` | [320] x 29b | 148,480 | 18,560 | mutable (clocked write) |
| 30 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.FF.replay.core.integer_path.queries[0].core.accum` (+12 more instances) | `taalas_generic_integer_projection` | [320] x 29b | 120,640 | 15,080 | mutable (clocked write) |

### Top 30 mutable arrays

ROM dominates the list above, so the 30 largest mutable arrays are listed separately.

| # | Hierarchical path | Module (orig) | Dims | Bits (all instances) | Bytes |
|---:|---|---|---|---:|---:|
| 1 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.history_nexus.history_payload.committed` | `rv_compact_history_storage_v1` | [4356] x 256b | 1,115,136 | 139,392 |
| 2 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.keys` | `taalas_compact_history_layer_self_o_q1` | [21120] x 32b | 675,840 | 84,480 |
| 3 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.values` | `taalas_compact_history_layer_self_o_q1` | [21120] x 32b | 675,840 | 84,480 |
| 4 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.bridge.feature_bank` | `rv_frontend_encoder_bridge` | [20480] x 32b | 655,360 | 81,920 |
| 5 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.backend.banks.bank0` | `rv_encoder_bank_consumer_edge_v1` | [2560] x 256b | 655,360 | 81,920 |
| 6 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.backend.banks.bank1` | `rv_encoder_bank_consumer_edge_v1` | [2560] x 256b | 655,360 | 81,920 |
| 7 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.producer_nexus.bank.bankA` | `rv_producer_mutable_storage_v1` | [2560] x 256b | 655,360 | 81,920 |
| 8 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.producer_nexus.bank.bankB` | `rv_producer_mutable_storage_v1` | [2560] x 256b | 655,360 | 81,920 |
| 9 | `TOP.original.frontend_nexus.banks.region6` | `rv_frontend_mutable_storage_v3` | [7680] x 32b | 245,760 | 30,720 |
| 10 | `TOP.original.frontend_nexus.banks.region2` | `rv_frontend_mutable_storage_v3` | [6400] x 32b | 204,800 | 25,600 |
| 11 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.backend.banks.bank2` | `rv_encoder_bank_consumer_edge_v1` | [640] x 256b | 163,840 | 20,480 |
| 12 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.producer_nexus.bank.bankCodes` | `rv_producer_mutable_storage_v1` | [640] x 256b | 163,840 | 20,480 |
| 13 | `TOP.original.frontend_nexus.banks.region3` | `rv_frontend_mutable_storage_v3` | [5120] x 32b | 163,840 | 20,480 |
| 14 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.endpoint.projector.core.integer_path.queries[0].core.accum` (+15 more instances) | `rv_q8_generic_integer_projection_attention_v1` | [320] x 29b | 148,480 | 18,560 |
| 15 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.FF.replay.core.integer_path.queries[0].core.accum` (+12 more instances) | `taalas_generic_integer_projection` | [320] x 29b | 120,640 | 15,080 |
| 16 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.attention_o.attention.head_owner.k` | `taalas_decoder_self_attention_q1` | [2640] x 32b | 84,480 | 10,560 |
| 17 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.attention_o.attention.head_owner.v` | `taalas_decoder_self_attention_q1` | [2640] x 32b | 84,480 | 10,560 |
| 18 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.prefix.heads.producer.attention.k_store` | `rv_frames_taalas_attention_head_query_stream` | [2560] x 32b | 81,920 | 10,240 |
| 19 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.prefix.heads.producer.attention.v_store` | `rv_frames_taalas_attention_head_query_stream` | [2560] x 32b | 81,920 | 10,240 |
| 20 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.FF.replay.hidden_codes` | `rv_frames_taalas_encoder_ff_presummed_down_q8` | [10240] x 8b | 81,920 | 10,240 |
| 21 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.p_owner.c_owner.attention_output.attention.head_owner.k` | `rv_frames_taalas_decoder_cross_variable_attention_q1` | [2560] x 32b | 81,920 | 10,240 |
| 22 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.p_owner.c_owner.attention_output.attention.head_owner.v` | `rv_frames_taalas_decoder_cross_variable_attention_q1` | [2560] x 32b | 81,920 | 10,240 |
| 23 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.prefix.normalized_codes.row_operator.learned_scales` (+4 more instances) | `taalas_encoder_residual_norm_scale` | [320] x 32b | 51,200 | 6,400 |
| 24 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.prefix.normalized_codes.row_operator.final_row` (+4 more instances) | `taalas_encoder_residual_norm_scale` | [320] x 32b | 51,200 | 6,400 |
| 25 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.prefix.normalized_codes.row_operator.core.input_row` (+4 more instances) | `taalas_encoder_norm320` | [320] x 32b | 51,200 | 6,400 |
| 26 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.prefix.normalized_codes.row_operator.core.result_row` (+4 more instances) | `taalas_encoder_norm320` | [320] x 32b | 51,200 | 6,400 |
| 27 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.endpoint.projector.input_values` (+1 more instances) | `rv_frames_taalas_attention_o_fixed_row_q8` | [2560] x 8b | 40,960 | 5,120 |
| 28 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.endpoint.projector.core.integer_path.queries[0].core.coefficient` (+15 more instances) | `rv_q8_generic_integer_projection_attention_v1` | [320] x 8b | 40,960 | 5,120 |
| 29 | `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.p_owner.f_owner.scratch` | `taalas_decoder_ff_q1` | [1280] x 32b | 40,960 | 5,120 |
| 30 | `TOP.original.frontend_nexus.banks.region7` | `rv_frontend_mutable_storage_v3` | [1280] x 32b | 40,960 | 5,120 |

Remaining 114 mutable array declarations total 599,802 bits (74,975.2 bytes). Full list in `inventory.json` → `all_mutable_arrays`.

### Case-statement LUT ROMs (functions / always @* with >=16 constant rows)

| Module | Function / target | Rows | Width | Instances | Bytes | Call sites in module | Source |
|---|---|---:|---:|---:|---:|---:|---|
| `rv_tied_index_service_v1` | `frozen_row` | 40,960 | 1024 | 1 | 5,242,880 | 2 | `rv_tied_index_service_v1.sv:22` |
| `rv_tied_book_loader_v3` | `frozen_beat` | 81,920 | 256 | 1 | 2,621,440 | 9 | `rv_tied_book_loader_v3.sv:68` |
| `rv_source_KV_book_index_service_v1` | `immutable_block` | 19,200 | 384 | 1 | 921,600 | 1 | `rv_source_KV_book_index_service_v1.sv:22` |
| `rv_producer_metadata_rom_service_v1` | `model_packet` | 960 | 256 | 1 | 30,720 | 1 | `rv_producer_metadata_rom_service_v1.sv:23` |
| `rv_decoder_learned_norm_readout_v1` | `immutable_row` | 1,920 | 128 | 1 | 30,720 | 1 | `rv_decoder_learned_norm_readout_v1.sv:34` |
| `taalas_asinh_host` | `coefficient` | 286 | 64 | 1 | 2,288 | 3 | `taalas_asinh_coefficients.vh:3` |
| `taalas_head_shared_consumer` | `product_pointer` | 256 | 7 | 8 | 1,792 | 32 | `taalas_head_shared_consumer.sv:299` |
| `taalas_embedding_dq_lut` | `value` | 256 | 32 | 1 | 1,024 | n/a (always @*) | `taalas_embedding_dq_lut.sv:3` |
| `taalas_asinh_host` | `instruction` | 36 | 37 | 1 | 166.5 | 1 | `taalas_asinh_program.vh:3` |

### Mutable array bytes by module

| Module (orig) | Bytes |
|---|---:|
| `rv_encoder_bank_consumer_edge_v1` | 184,320 |
| `rv_producer_mutable_storage_v1` | 184,320 |
| `taalas_compact_history_layer_self_o_q1` | 170,240 |
| `rv_compact_history_storage_v1` | 141,504 |
| `rv_frontend_encoder_bridge` | 81,920 |
| `rv_frontend_mutable_storage_v3` | 81,920 |
| `rv_q8_generic_integer_projection_attention_v1` | 24,096 |
| `rv_frames_taalas_attention_head_query_stream` | 21,850 |
| `taalas_decoder_self_attention_q1` | 21,729 |
| `taalas_generic_integer_projection` | 21,266 |
| `rv_frames_taalas_decoder_cross_variable_attention_q1` | 21,081 |
| `rv_frames_taalas_encoder_ff_presummed_down_q8` | 15,680 |
| `taalas_encoder_residual_norm_scale` | 12,800 |
| `taalas_encoder_norm320` | 12,800 |
| `taalas_decoder_ff_q1` | 9,280 |
| `rv_frames_taalas_attention_o_fixed_row_q8` | 8,832 |
| `rv_frames_taalas_decoder_layer_compact_q1` | 7,680 |
| `rv_frames_taalas_encoder_head40_query_stream_layers_q8` | 7,360 |
| `taalas_head_shared_consumer` | 3,392 |
| `taalas_decoder_norm_q_q1` | 3,200 |

### Register bits by module (top 20)

| Module (orig) | Register bits (all instances) |
|---|---:|
| `taalas_book_page_cache` | 73,800 |
| `taalas_shared_fp32_fma_pipeline` | 24,576 |
| `divSqrtRecFNToRaw_small` | 20,991 |
| `taalas_dql_value` | 9,856 |
| `taalas_dynamic_fp32_fma` | 8,864 |
| `taalas_dql_divide` | 7,683 |
| `rv_frames_taalas_attention_o_fixed_row_q8` | 5,656 |
| `taalas_dql_sealed_source_q32` | 3,984 |
| `rv_frames_taalas_encoder_ff_presummed_down_q8` | 3,725 |
| `taalas_fp32_affine_bank` | 3,258 |
| `taalas_encoder_erf` | 3,256 |
| `taalas_decoder_shared_domain_q1` | 3,088 |
| `taalas_decoder_ff_q1` | 2,849 |
| `taalas_decoder_norm_q_q1` | 2,797 |
| `rv_frames_taalas_decoder_cross_o_q1` | 2,708 |
| `taalas_decoder_self_o_q1` | 2,706 |
| `rv_source_KV_book_index_service_v1` | 2,705 |
| `rv_onchip_encoder_O_v1` | 2,609 |
| `rv_tied_index_service_v1` | 2,149 |
| `taalas_dql_retirable_source_q32` | 1,993 |

### Largest individual registers (top 15)

| Path | Module | Width | Instances | Total bits |
|---|---|---:|---:|---:|
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.h.head.head.tiles[0].core.lane_0.sum_latch` (+255 more instances) | `taalas_shared_fp32_fma_pipeline` | 49 | 256 | 12,544 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.h.head.head.tiles[0].core.lane_0.high_latch` (+255 more instances) | `taalas_shared_fp32_fma_pipeline` | 26 | 256 | 6,656 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.frontend.frontend.child.dense.convolution_chain.activation.gate.divide.out_value` (+196 more instances) | `taalas_dql_divide` | 32 | 197 | 6,304 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.prefix.normalized_codes.quantizer.bank.lanes[0].value_lane.quotient` (+175 more instances) | `taalas_dql_value` | 32 | 176 | 5,632 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.frontend.frontend.child.preprocess.child.cmvn.divider.d.divSqrtRecFNToRaw.rem_Z` (+207 more instances) | `divSqrtRecFNToRaw_small` | 26 | 208 | 5,408 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.frontend.frontend.child.preprocess.child.cmvn.divider.d.divSqrtRecFNToRaw.sigX_Z` (+207 more instances) | `divSqrtRecFNToRaw_small` | 26 | 208 | 5,408 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.endpoint.projector.coefficient_buffer` (+1 more instances) | `rv_frames_taalas_attention_o_fixed_row_q8` | 2560 | 2 | 5,120 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.frontend.frontend.child.preprocess.child.cmvn.divider.d.divSqrtRecFNToRaw.fractB_Z` (+207 more instances) | `divSqrtRecFNToRaw_small` | 23 | 208 | 4,784 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.upstream.encoder.layer_owner.FF.replay.coefficients` | `rv_frames_taalas_encoder_ff_presummed_down_q8` | 2560 | 1 | 2,560 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.p_owner.c_owner.query_producer.coefficients` | `taalas_decoder_norm_q_q1` | 2560 | 1 | 2,560 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.p_owner.c_owner.attention_output.coefficients` | `rv_frames_taalas_decoder_cross_o_q1` | 2560 | 1 | 2,560 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.p_owner.f_owner.coefficient_buffer` | `taalas_decoder_ff_q1` | 2560 | 1 | 2,560 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.owner.leaf.coefficients` | `taalas_decoder_shared_domain_q1` | 2560 | 1 | 2,560 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.b.compact_owner.attention_o.coefficients` | `taalas_decoder_self_o_q1` | 2560 | 1 | 2,560 |
| `TOP.original.sole_qualified_neural_parent.sole_neural_parent.existing_parent.qualified_child.qualified_child.downstream.decoder.producer.token.h.head.head.tiles[0].core.lane_0.exponent_latch` (+255 more instances) | `taalas_shared_fp32_fma_pipeline` | 10 | 256 | 2,560 |

## Classification method

- Every `VAR` in every elaborated module (including generate blocks; function/task locals excluded) is sized from the resolved dtype table: unpacked dims x packed width.
- Write contexts are found from `VARREF` nodes with `access=WR` on assignment left-hand sides: inside `ALWAYS` with an edge sensitivity (clocked), other `ALWAYS`/`ASSIGNW` (combinational), `INITIAL` (initial), `READMEM` target, or child-cell output pins.
- ROM = written only by `$readmemh` in `initial` (or only by initial constants) and never in a clocked/combinational process. Mutable = written in a clocked process. Register = non-array variable with a non-blocking write in a clocked process.
- Case-LUT ROM = a `case` whose items are single constant assignments (>=16 rows), counted as rows x target width (default item excluded).
- Instance counts come from walking `CELL -> modp` from the top; every parameter specialisation is a separate module in the elaborated tree.

Class totals (all variables, all instances):

| Class | Kind | Vars | Var instances | Bits |
|---|---|---:|---:|---:|
| rom_readmem | array | 17 | 17 | 229,130,240 |
| param | scalar/vector | 2,120 | 305,331 | 9,632,412 |
| flop | array | 144 | 321 | 8,501,818 |
| combinational | scalar/vector | 13,930 | 503,246 | 7,674,288 |
| input_port | scalar/vector | 4,003 | 80,108 | 1,364,662 |
| combinational | array | 92 | 705 | 360,929 |
| flop | scalar/vector | 2,977 | 18,380 | 237,521 |
| constant_net | scalar/vector | 128 | 11,392 | 90,039 |
| clocked_blocking_only | scalar/vector | 27 | 74 | 2,368 |
| automatic | scalar/vector | 13 | 15 | 480 |
| undriven_or_child_driven | scalar/vector | 3 | 10 | 112 |
| mutable_initialised | scalar/vector | 3 | 3 | 3 |

(`param` = localparam/parameter constants, `constant_net` = constant assigns that Verilator folded to initial; neither is storage.)

## (c) Commands used

```sh
nice -n 15 /opt/homebrew/bin/verilator --json-only --json-only-output /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/storage-inventory/vobj/top.tree.json --json-only-meta-output /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/storage-inventory/vobj/top.tree.meta.json -Wno-fatal --top-module rv_allonchip_top_all_v1 -I/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/third_party/hardfloat/HardFloat-1/source -I/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/third_party/hardfloat/HardFloat-1/source/ARM-VFPv2 -I/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/rtl --Mdir /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/storage-inventory/vobj \
  $(python3 -c "import json;print(' '.join(a for a in json.load(open('../onchip-all/commands.json'))['lint-full'] if a.endswith(('.sv','.v'))))")   # the 151 source files of onchip-all/commands.json lint-full, same order
nice -n 15 python3 analyze.py vobj/top.tree.json vobj/top.tree.meta.json vobj/rows.json
python3 report.py
```

Verilator output: `storage-inventory/vobj/top.tree.json (175 MB, gzipped afterwards to top.tree.json.gz to save disk), top.tree.meta.json(.gz), json.log; analyze.py needs them gunzipped`. 169 `TIMESCALEMOD` warnings, no errors. Full argv as a list in `commands-used.json`.

## (d) Caveats

- **RTL logical bits, not physical.** Synthesis may remove, merge or retime state. Nothing here is from synthesis; the earlier Yosys run in `synth/` was terminated and is for the base top.
- **Registers are an upper-bound-ish RTL count.** A non-blocking write in a clocked block is counted as a flop even if the value is constant or never read (synthesis would remove it). Blocking-only temporaries in clocked blocks (mostly loop indices, 2,368 bits) are excluded. Latches inferred from incomplete `always @*` blocks are not detected (Verilator only checks `always_comb` for LATCH and reported none).
- **Wide packed vectors used as buffers** (e.g. 2,560-bit `coefficient_buffer`, 1,024-bit packets) and register files built from generate-loop scalars (e.g. `taalas_book_page_cache`, 73,800 bits over 9 instances as `columns[i].entries[j].value0/1` + `tags`) are counted in register bits, not mutable arrays.
- **Mutable arrays include all instantiated legacy storage.** E.g. encoder bank0/1/2, producer bankA/B/Codes, compact-history `committed`, frontend mutable regions. Whether any of these are now redundant after the weights moved on-chip was not judged; they are still instantiated and written.
- **Case-LUT ROM call sites.** `frozen_beat` (book loader) is called from 9 sites and `product_pointer` from 32; synthesis might duplicate that decode logic. The bytes above count each table once per module instance.
- **ROM is logical payload.** `$readmemh` arrays are sized by declaration (they match the ROM manifest exactly). Physical ROM macro area, word organisation and peripheral circuits are not measured.
- Classification relies on Verilator `access` flags and process sensitivities in the `--json-only` tree (after V3Param/V3Width, before flattening). Hierarchical (`VARXREF`) writes: none found. Function-local statics are excluded.
- Paths show one representative instance; `(+N more instances)` means the same module specialisation is instantiated N+1 times and the bits are multiplied accordingly.
