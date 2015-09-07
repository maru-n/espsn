SETTING_GENERATOR="../../setting_generator.py"
WORK_DIR="~/espsn/scripts/N-T_search"
ESPSN="./espsn"

INIT_TIME=10
EVAL_TIME=100

for N in `seq 8 8 64`
do
    qsub_script=`printf "N%02d_qsub-run.sh" $N`
    echo "#!/bin/sh" > $qsub_script
    echo "#PBS -l walltime=60:00:00" >> $qsub_script
    echo "cd ${WORK_DIR}" >> $qsub_script

    for T in `seq 200 200 1600`
    do
        init=$INIT_TIME
        duration=`expr $T + $INIT_TIME + $EVAL_TIME`
        training=`expr $T + $INIT_TIME`
        setting_file=`printf "N%02d-T%04d_settings.txt" $N $T`
        output_file=`printf "N%02d-T%04d" $N $T`
        echo "N:${N} T:${T}"
        python $SETTING_GENERATOR \
        -o $setting_file \
        -N $N \
        --duration $duration \
        --init-time $init \
        --training-time $training \
        --one-signal-duration 1 \
        --random-seed 1234 \
        -t delay

        echo "${ESPSN} -o ${output_file} ${setting_file}" >> $qsub_script
        #echo "rm ${output_file}.tcp" >> $qsub_script
    done
done
