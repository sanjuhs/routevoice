from pathlib import Path
import numpy as np,json
W=Path(__file__).resolve().parent
z=np.load(W/'vectors/model.npz');weights=z['weights'].astype(np.int64);zp=z['zero'].astype(np.int64)
d={'scope':'Worst-case absolute bounds for independently chosen centered activation integers in [-255,255], over the fixed selected matrix. Does not prove control or physical timing.','shared_radix16_partial_max_abs':255*15,'shared_partial_signed_bits':13,'UINT8_product_max_abs':255*255,'product_signed_bits':17,'uncorrected_accumulator_max_abs':int((255*weights.sum(axis=0)).max()),'uncorrected_accumulator_signed_bits':27,'uncorrected_accumulator_positive_limit':2**26-1,'zero_point_correction_max_abs':int(255*1280*zp.max()),'corrected_dot_max_abs':int((255*np.abs(weights-zp).sum(axis=0)).max()),'corrected_output_signed_bits':32}
assert d['shared_radix16_partial_max_abs']<2**12 and d['UINT8_product_max_abs']<2**16 and d['uncorrected_accumulator_max_abs']<2**26 and d['corrected_dot_max_abs']<2**31
(W/'evidence/numerical-width-bounds.json').write_text(json.dumps(d,indent=2)+'\n')
print('W2b-STATUS: Selected-matrix integer width bounds PASS')
