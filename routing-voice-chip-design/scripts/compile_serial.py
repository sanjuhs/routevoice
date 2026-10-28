#!/usr/bin/env python3
"""Exact frozen-weight dot products with bit-serial, signed activation transport."""
import json,sys
from pathlib import Path
from compile_tile import compile_matrix

def compile_serial(name, weights, input_bits=9,weight_bits=9):
    _,meta=compile_matrix(name,weights,input_bits,weight_bits)
    n=meta['inputs'];m=meta['outputs'];w=meta['accumulator_bits']
    bitw=(input_bits-1).bit_length();sumw=1+(n*(1<<(weight_bits-1))).bit_length()
    lines=[f'module {name} (input wire clk, input wire rst_n,',
           'input wire in_valid, output wire in_ready,',f'input wire [{n*input_bits-1}:0] in_data,',
           'output reg out_valid, input wire out_ready,',f'output reg [{m*w-1}:0] out_data);',
           'reg busy;',f'reg [{bitw-1}:0] bit_index;',f'reg [{n*input_bits-1}:0] data_q;',
           'assign in_ready = !busy && (!out_valid || out_ready);']
    for i,row in enumerate(weights):
        terms=[]
        for j,v in enumerate(row):
            const=f"{sumw}'sd{abs(v)}";const=f'(-{const})' if v<0 else const
            if v:terms.append(f'(data_q[{j*input_bits}+bit_index] ? {const} : {sumw}\'sd0)')
        def tree(ts):
            if not ts:return f"{sumw}'sd0"
            if len(ts)==1:return ts[0]
            k=len(ts)//2;return '('+tree(ts[:k])+' + '+tree(ts[k:])+')'
        lines += [f'reg signed [{w-1}:0] acc{i};',f'wire signed [{sumw-1}:0] plane{i} = {tree(terms)};',
                  f'wire signed [{w-1}:0] extended{i} = {{{{{w-sumw}{{plane{i}[{sumw-1}]}}}},plane{i}}};',
                  f'wire signed [{w-1}:0] next{i} = bit_index == {input_bits-1} ? -extended{i} : ((acc{i} <<< 1) + extended{i});']
    lines += ['always @(posedge clk) begin','if (!rst_n) begin busy<=0; out_valid<=0; out_data<=0; data_q<=0; bit_index<=0;']
    lines += [f'acc{i}<=0;' for i in range(m)]
    lines += ['end else begin','if (out_valid && out_ready) out_valid<=0;',
              f'if (in_valid && in_ready) begin data_q<=in_data; bit_index<={input_bits-1}; busy<=1; end',
              'if (busy) begin']
    lines += [f'acc{i}<=next{i};' for i in range(m)]
    lines += ['if (bit_index == 0) begin busy<=0; out_valid<=1;']
    lines += [f'out_data[{i*w} +: {w}]<=next{i};' for i in range(m)]
    lines += ['end else bit_index<=bit_index-1;', 'end','end','end','endmodule','']
    meta.update(architecture='bit-serial activations, fixed coefficients',latency_cycles=input_bits,initiation_interval_cycles=input_bits+1)
    return '\n'.join(lines),meta

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    for p in sorted((root/'models').glob('die*_tile.json')):
        obj=json.loads(p.read_text());name=obj['name']+'_serial';rtl,meta=compile_serial(name,obj['weights'],obj['input_bits'],obj['weight_bits'])
        (root/'rtl'/f'{name}.sv').write_text(rtl);(root/'reports'/f'{name}-compile.json').write_text(json.dumps(meta,indent=2)+'\n')
