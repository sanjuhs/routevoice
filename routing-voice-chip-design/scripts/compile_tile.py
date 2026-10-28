#!/usr/bin/env python3
"""Compile a frozen signed 8/9-bit matrix into registered constant shift/add RTL.
Input JSON: {name: identifier, weights: [output][input] signed integers}.
No quantization is inferred: output is the exact integer dot product.
"""
import argparse
import json
import math
import re
from pathlib import Path


def compile_matrix(name, weights, input_bits=8, weight_bits=8):
    if input_bits not in (8, 9) or weight_bits not in (8, 9):
        raise ValueError("Supported operand widths are 8 or 9 bits")
    if not re.fullmatch(r'[a-zA-Z_][a-zA-Z_0-9]*', name):
        raise ValueError('Invalid module identifier')
    if not weights or not weights[0]:
        raise ValueError('Empty matrix')
    n = len(weights[0]); m = len(weights)
    if any(len(row) != n for row in weights):
        raise ValueError('Ragged matrix')
    if any(type(w) is not int or not -(1 << (weight_bits-1)) <= w < (1 << (weight_bits-1)) for row in weights for w in row):
        raise ValueError('Weights exceed the declared signed width')
    # Include the positive product of two most-negative signed operands.
    width = 1 + ((1 << (input_bits + weight_bits - 2)) * n).bit_length()
    lines = [f'module {name} (', ' input wire clk, input wire rst_n,',
             ' input wire in_valid, output wire in_ready,',
             f' input wire [{n*input_bits-1}:0] in_data,',
             ' output reg out_valid, input wire out_ready,',
             f' output reg [{m*width-1}:0] out_data', ');',
             ' assign in_ready = !out_valid || out_ready;']
    for j in range(n):
        lines.append(f' wire signed [{width-1}:0] x{j} = {{{{{width-input_bits}{{in_data[{j*input_bits+input_bits-1}]}}}}, in_data[{j*input_bits} +: {input_bits}]}};')
    def balanced(terms):
        if not terms: return f"{width}'sd0"
        if len(terms)==1: return terms[0]
        k=len(terms)//2
        return '('+balanced(terms[:k])+' + '+balanced(terms[k:])+')'
    for i,row in enumerate(weights):
        terms=[]
        for j,w in enumerate(row):
            if not w: continue
            term=balanced([f'(x{j} <<< {bit})' for bit in range(weight_bits) if abs(w)&(1<<bit)])
            terms.append(f'(-{term})' if w<0 else term)
        lines.append(f' wire signed [{width-1}:0] y{i} = {balanced(terms)};')
    lines += [' always @(posedge clk) begin', "  if (!rst_n) begin out_valid <= 1'b0; out_data <= 0; end",
              '  else if (in_ready) begin', '   out_valid <= in_valid;', '   if (in_valid) begin']
    for i in range(m): lines.append(f'    out_data[{i*width} +: {width}] <= y{i};')
    lines += ['   end', '  end', ' end', 'endmodule', '']
    return '\n'.join(lines), {'inputs':n,'outputs':m,'input_bits':input_bits,'weight_bits':weight_bits,'accumulator_bits':width,'weight_storage_bits':0,'coefficients':m*n,'nonzero_coefficients':sum(w!=0 for row in weights for w in row),'latency_cycles':1,'initiation_interval_cycles':1,'interface':'single clock ready/valid; output holds under backpressure; synchronous active-low reset'}


def main():
    p=argparse.ArgumentParser();p.add_argument('matrix',type=Path);p.add_argument('rtl',type=Path);a=p.parse_args()
    obj=json.loads(a.matrix.read_text()); rtl,meta=compile_matrix(obj['name'],obj['weights'],obj.get('input_bits',8),obj.get('weight_bits',8))
    a.rtl.parent.mkdir(parents=True,exist_ok=True);a.rtl.write_text(rtl)
    a.rtl.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')

if __name__=='__main__':main()
