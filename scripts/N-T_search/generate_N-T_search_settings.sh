SETTING_GENERATOR="../../setting_generator.py"
WORK_DIR="~/espsn/scripts/N-T_search"
ESPSN="./espsn"

for N in `seq 8 8 64`
do
    for T in `seq 100 200 500`
    do
        duration=`expr $T + 100 + 500`
        setting_file=`printf "N%02d-T%04d_settings.txt" $N $T`
        output_file=`printf "N%02d-T%04d" $N $T`
        echo "N:${N} T:${T}"
        python $SETTING_GENERATOR \
        -o $setting_file \
        -N $N \
        --duration $duration \
        --init-time 100 \
        --training-time $T \
        --one-signal-duration 1 \
        --random-seed 1234 \
        -t delay

        qsub_script=`printf "N%02d-T%04d_qsub-run.sh" $N $T`
        echo "#!/bin/sh" > $qsub_script
        echo "#PBS -l walltime=60:00:00" >> $qsub_script
        echo "cd ${WORK_DIR}" >> $qsub_script
        echo "${ESPSN} -o ${output_file} ${setting_file}" >> $qsub_script
    done
done
