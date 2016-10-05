trainBinPath="`dirname \"$0\"`"
syntaxnet=/home/admin16/Documents/models
sweconlls=/home/admin16/Documents/UD_Swedish
export TEST_SRCDIR=$syntaxnet/syntaxnet/bazel-bin
export CONTEXTDIR=$sweconlls/


python $syntaxnet/syntaxnet/syntaxnet/convert.py < "$sweconlls/sv-ud-train.conllu" > "$sweconlls/train.conll"
python $syntaxnet/syntaxnet/syntaxnet/convert.py < "$sweconlls/sv-ud-test.conllu" > "$sweconlls/test.conll"
python $syntaxnet/syntaxnet/syntaxnet/convert.py < "$sweconlls/sv-ud-dev.conllu" > "$sweconlls/dev.conll"

"$trainBinPath/parser_trainer_test_swe.sh" models/swedish-ud-
