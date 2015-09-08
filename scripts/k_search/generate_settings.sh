SETTING_GENERATOR="../../setting_generator.py"
WORK_DIR="~/espsn/scripts/k_search"
ESPSN="./espsn"

INIT_TIME=10
EVAL_TIME=100

for k in `seq 1 1 15`
do
    qsub_script=`printf "k%02d_qsub-run.sh" $k`
    echo "#!/bin/sh" > $qsub_script
    echo "#PBS -l walltime=60:00:00" >> $qsub_script
    echo "cd ${WORK_DIR}" >> $qsub_script

    N=16
    init=$INIT_TIME
    duration=710
    training=510
    output_file=`printf "k%02d" ${k}`
    setting_file="${output_file}_settings.txt"
    echo "k:${k}"
    python $SETTING_GENERATOR \
        -o $setting_file \
        -N $N \
        --duration $duration \
        --init-time $init \
        --training-time $training \
        --one-signal-duration 1 \
        --random-seed 1234 \
        -k $k \
        -t delay

    echo "${ESPSN} -o ${output_file} ${setting_file}" >> $qsub_script
        #echo "rm ${output_file}.tcp" >> $qsub_script
done
