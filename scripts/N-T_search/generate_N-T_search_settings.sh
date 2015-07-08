SETTING_GENERATOR="../../setting_generator.py"
WORK_DIR="~/test"

for N in `seq 4 4 64`
do
    for T in `seq 100 100 1000`
    do
        duration=`expr $T + 100 + 500`
        setting_file=`printf "N%02d-T%04d_settings.txt" $N $T`
        qsub_script=`printf "N%02d-T%04d_qsub-run.sh" $N $T`
        output_file=`printf "N%02d-T%04d" $N $T`
        echo $setting_file
        python $SETTING_GENERATOR \
        -o $setting_file \
        -N $N \
        --duration $duration \
        --init-time 100 \
        --training-time $T \
        --one-signal-duration 1 \
        --random-seed 1234 \
        -t delay

        echo "#!/bin/sh" > $qsub_script
        echo "#PBS -l walltime=60:00:00" >> $qsub_script
        echo "cd ${WORK_DIR}" >> $qsub_script
        echo "espsn -o ${output_file} ${setting_file}" >> $qsub_script
    done
done
