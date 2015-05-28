for i in `seq 2 40`
do
    echo "###############"
    echo "N: ${i}"
    echo "###############"
    DIR="data/xor_N-${i}"
    mkdir $DIR
    ./setting_generator.py -N $i
    mv settings.txt $DIR
    ./espsn "${DIR}/settings.txt"
done
