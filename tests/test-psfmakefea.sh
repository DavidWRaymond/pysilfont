# this test script uses the Charis Reg UFO
# clone the Charis repo and checkout the commit indicated by Charis-test-commit-SHA.txt
#  in a directory parallel to pysilfont
# after the tests run, compare the generated files to their *-ref counterparts

# cd ../..
# git clone https://github.com/silnrsi/font-charis.git
# cd font-charis
# git checkout < ../pysilfont/tests/Charis-test-commit-SHA.txt #this does NOT work
# cd ../pysilfont/tests

# test class generation only
python ../lib/silfont/scripts/psfmakefea.py ../../font-charis/source/CharisSIL-Regular.ufo -o results/classes.fea

# test the use of a base class in a position lookup
python ../lib/silfont/scripts/psfmakefea.py ../../font-charis/source/CharisSIL-Regular.ufo -o results/test-baseClass.fea -i test-baseClass.feax

# test that the Charis fea will pass thru cleanly
# *** this will OVERWRITE any features.fea that is already present in the UFO
# at this time, no such file is present
#  the fea compilation typically starts with a file generated by make_fea in results/source
cp Charis-Reg-make_fea.fea ../../font-charis/source/CharisSIL-Regular.ufo/features.fea
python ../lib/silfont/scripts/psfmakefea.py ../../font-charis/source/CharisSIL-Regular.ufo -o results/features.fea  -i ../../font-charis/source/CharisSIL-Regular.ufo/features.fea
rm ../../font-charis/source/CharisSIL-Regular.ufo/features.fea

# this FAILS because the includes in the CharisSIL-Regular.fea are written assuming
#  that that file is itself included from source/results
# python ../lib/silfont/scripts/psfmakefea.py ../../font-charis/source/CharisSIL-Regular.ufo -o results/features.fea  -i ../../font-charis/source/opentype/CharisSIL-Regular.fea

diff results/classes.fea results/classes-ref.fea
diff results/test-baseClass.fea results/test-baseClass-ref.fea
diff results/features.fea results/features-ref.fea