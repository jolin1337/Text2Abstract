#!/bin/bash
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# A script that runs a tokenizer, a part-of-speech tagger and a dependency
# parser on an English text file, with one sentence per line.
#
# Example usage:
#  echo "Parsey McParseface is my favorite parser!" | syntaxnet/demo.sh

# To run on a conll formatted file, add the --conll command line argument.
#

#BIN=../../models/syntaxnet/syntaxnet/
BIN=/home/admin16/Documents/models/syntaxnet/bazel-bin/syntaxnet/
MODEL_DIR=/home/admin16/Documents/AI-journalisten/syntaxnet/models
[[ "$1" == "--conll" ]] && INPUT_FORMAT=stdin-conll || INPUT_FORMAT=stdin

$BIN/parser_eval \
  --input=$INPUT_FORMAT \
  --output=stdout-conll \
  --hidden_layer_sizes=128 \
  --arg_prefix=brain_pos \
  --graph_builder=greedy \
  --task_context=$MODEL_DIR/brain_pos/greedy/128-0.08-3600-0.9-1/context \
  --model_path=$MODEL_DIR/tagger-params \
  --slim_model \
  --batch_size=1024 \
  --alsologtostderr \
   | \
  $BIN/parser_eval \
  --input=stdin-conll \
  --output=stdout-conll \
  --hidden_layer_sizes=200,200 \
  --arg_prefix=brain_parser \
  --graph_builder=structured \
  --task_context=$MODEL_DIR/brain_pos/greedy/128-0.08-3600-0.9-1/context \
  --model_path=$MODEL_DIR/parser-params \
  --slim_model \
  --batch_size=32 \
  --alsologtostderr \
  #| \
  #$BIN/conll2tree \
  #--task_context=$MODEL_DIR/brain_pos/greedy/128-0.08-3600-0.9-1/context \
  #--alsologtostderr




  # $MODEL_DIR/brain_pos/greedy/128-0.08-3600-0.9-1/context \
