trainBinPath="`dirname \"$0\"`"
syntaxnet=/home/admin16/Documents/models
sweconlls=/home/admin16/Documents/talbanken-dep
export TEST_SRCDIR=$syntaxnet/syntaxnet/bazel-bin
export CONTEXTDIR=$sweconlls/

cp $sweconlls/talbanken-dep-train.conll $sweconlls/train.conll
cp $sweconlls/talbanken-dep-test.conll $sweconlls/test.conll
#python $syntaxnet/syntaxnet/syntaxnet/convert.py < "$sweconlls/talbanken-dep-train.conllu" > "$sweconlls/train.conll"
#python $syntaxnet/syntaxnet/syntaxnet/convert.py < "$sweconlls/talbanken-dep-test.conllu" > "$sweconlls/test.conll"
#python $syntaxnet/syntaxnet/syntaxnet/convert.py < "$sweconlls/talbanken-dep-dev.conllu" > "$sweconlls/dev.conll"

$trainBinPath/parser_trainer_test_swe.sh models/talbanken-dep
