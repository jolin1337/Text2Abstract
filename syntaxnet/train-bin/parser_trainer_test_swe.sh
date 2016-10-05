
set -eu #x - write commands on screen

if [ -z ${TEST_SRCDIR+x} ]; then
   echo "You must set the \$TEST_SRCDIR environment variable"
   exit
fi
if [ -z ${CONTEXTDIR+x} ]; then
   echo "You must set the \$CONTEXTDIR environment variable"
   exit
fi

BINDIR=$TEST_SRCDIR/syntaxnet
CONTEXT=$CONTEXTDIR/context.pbtxt     #$BINDIR/testdata/context.pbtxt
TMP_DIR=/tmp/syntaxnet-swe-output

# Converts SRCDIR and OUTPATH to the TEST_SRCDIR and TMP_DIR respectively
#mkdir -p $TMP_DIR
#sed "s=SRCDIR=$TEST_SRCDIR=" "$CONTEXT" | \
#  sed "s=OUTPATH=$TMP_DIR=" > $TMP_DIR/context

EPOCHS=8
PARAMS=128-0.08-3600-0.9-1
POS_TRAIN=true
POS_PARSE_TRAIN=true
MODEL_PREFIX=
echo $#
if [ "$#" -gt 0 ]; then
  MODEL_PREFIX=$1
fi
mkdir -p ${MODEL_PREFIX}models

#BASE="/home/admin16/Documents/UD_Swedish/"
#python ./syntaxnet/convert.py < "${BASE}sv-ud-train.conllu" > "${BASE}train.conll"
#python ./syntaxnet/convert.py < "${BASE}sv-ud-test.conllu" > "${BASE}test.conll"
#python ./syntaxnet/convert.py < "${BASE}sv-ud-dev.conllu" > "${BASE}dev.conll"

# A working trainer command
$POS_TRAIN && echo -e "\n\n-------------- Training the SyntaxNet POS Tagger ----------------------------"
$POS_TRAIN && "$BINDIR/parser_trainer" \
  --task_context=$CONTEXT \
  --compute_lexicon \
  --arg_prefix=brain_pos \
  --graph_builder=greedy \
  --training_corpus=train_file \
  --tuning_corpus=tune_file \
  --output_path=${MODEL_PREFIX}models \
  --batch_size=32 \
  --decay_steps=3600 \
  --hidden_layer_sizes=128 \
  --learning_rate=0.08 \
  --momentum=0.9 \
  --params=$PARAMS \
  --seed=13 \
  --num_epochs=$EPOCHS \



  #--arg_prefix=brain_pos \
  #--graph_builder=greedy \
$POS_TRAIN && echo -e "\n\n-------------- Preprocessing with the Tagger ----------------------------"
$POS_TRAIN && for SET in train tune dev; do
  "$BINDIR/parser_eval" \
    --task_context=${MODEL_PREFIX}models/brain_pos/greedy/$PARAMS/context \
    --hidden_layer_sizes=128 \
    --input=${SET}_file \
    --output=tagged_${SET}_file \
    --arg_prefix=brain_pos \
    --graph_builder=greedy \
    --model_path=${MODEL_PREFIX}models/brain_pos/greedy/$PARAMS/model
done

$POS_PARSE_TRAIN && echo -e "\n\n-------------- Training the Parser ----------------------------"

$POS_PARSE_TRAIN && echo -e "\n       Step 1: Local Pretraining"
$POS_PARSE_TRAIN && "$BINDIR/parser_trainer" \
  --task_context=${MODEL_PREFIX}models/brain_pos/greedy/$PARAMS/context \
  --arg_prefix=brain_parser \
  --graph_builder=greedy \
  --training_corpus=tagged_train_file \
  --tuning_corpus=tagged_tune_file \
  --output_path=${MODEL_PREFIX}models \
  --batch_size=32 \
  --decay_steps=3600 \
  --hidden_layer_sizes=200,200 \
  --learning_rate=0.02 \
  --momentum=0.85 \
  --params=$PARAMS \
  --seed=4 \
  --num_epochs=$EPOCHS \
  --projectivize_training_set 
#  --compute_lexicon \
$POS_PARSE_TRAIN && for SET in train tune dev; do
  "$BINDIR/parser_eval" \
    --task_context=${MODEL_PREFIX}models/brain_parser/greedy/$PARAMS/context \
    --hidden_layer_sizes=200,200 \
    --input=tagged_${SET}_file \
    --output=parsed_${SET}_file \
    --arg_prefix=brain_parser \
    --graph_builder=greedy \
    --model_path=${MODEL_PREFIX}models/brain_parser/greedy/$PARAMS/model
done

$POS_PARSE_TRAIN && echo -e "\n       Step 2: Global Training"
$POS_PARSE_TRAIN && "$BINDIR/parser_trainer" \
  --arg_prefix=brain_parser \
  --batch_size=8 \
  --decay_steps=100 \
  --graph_builder=structured \
  --hidden_layer_sizes=200,200 \
  --learning_rate=0.01 \
  --momentum=0.85 \
  --output_path=${MODEL_PREFIX}models \
  --task_context=${MODEL_PREFIX}models/brain_parser/greedy/$PARAMS/context \
  --seed=3 \
  --training_corpus=projectivized-training-corpus \
  --tuning_corpus=tagged_tune_file \
  --params=$PARAMS \
  --pretrained_params=${MODEL_PREFIX}models/brain_parser/greedy/$PARAMS/model \
  --num_epochs=$EPOCHS \
  --pretrained_params_names=\
embedding_matrix_0,embedding_matrix_1,embedding_matrix_2,\
bias_0,weights_0,bias_1,weights_1

$POS_PARSE_TRAIN && for SET in train tune dev; do
  "$BINDIR/parser_eval" \
    --task_context=${MODEL_PREFIX}models/brain_parser/structured/$PARAMS/context \
    --hidden_layer_sizes=200,200 \
    --input=tagged_${SET}_file \
    --output=beam-parsed_${SET}_file \
    --arg_prefix=brain_parser \
    --graph_builder=structured \
    --model_path=${MODEL_PREFIX}models/brain_parser/structured/$PARAMS/model
done

#mv $TMP_DIR/* ${MODEL_PREFIX}models/brain_parser/
#mv ${MODEL_PREFIX}models/brain_pos/greedy/$PARAMS/model ${MODEL_PREFIX}models/tagger-params
cd ${MODEL_PREFIX}models
ln -s brain_pos/greedy/$PARAMS/model tagger-params
ln -s brain_parser/structured/$PARAMS/model parser-params
cd -