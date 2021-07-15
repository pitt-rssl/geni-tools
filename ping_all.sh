#/bin/bash

# Reads lines from input file, where each line specifies a machine. For each
# machine, ssh into that machine, and ping all other machines (that we haven't
# yet measured).

# Expected input line format is:
# hostname host_IP ssh_options

function usage {
    usage1="Usage:"
    usage2=" -f <input_file> : input file containing list of machines to run on"

    printf "%s\n%s\n" "$usage1" "$usage2"

    exit 1
}

Machine_List=""

# Parse command line arguments
while getopts f:h opt
do
    case "$opt" in
        f) Machine_List=$OPTARG
           ;;
        h) usage
           ;;
        *) usage
           ;;
    esac
done

# Check that required args were provided
if [[ -z $Machine_List ]]
then
    usage
fi

# Read input file and build list to ping
echo "--- Reading machines from $Machine_List ---"
Machine_Names=()
Machine_IPs=()
SSH_Ops=()
num_mach=0
while read -r -a line
do
    mach_name=${line[0]}
    mach_ip=${line[1]}
    num_ops=$((${#line[@]}-2))
    ops=${line[@]:2:$num_ops}
    Machine_Names[$num_mach]=$mach_name
    Machine_IPs[$num_mach]=$mach_ip
    SSH_Ops[$num_mach]=$ops
    num_mach=$(($num_mach+1))
done < $Machine_List

for ((i=0; $i < $num_mach; i=$i+1))
do
    printf "\n\n==== ${Machine_Names[$i]} ${Machine_IPs[$i]} ====\n\n"
    source_name=${Machine_Names[$i]}
    source_ip=${Machine_IPs[$i]}
    ops=${SSH_Ops[$i]}

    for ((j=0; $j < $num_mach; j=$j+1))
    do
        if [[ $j -eq $i ]]
        then
            continue
        fi

        target_ip=${Machine_IPs[$j]}
        printf "\n**** PING ($(($i+1)), $(($j+1))) : $source_name -> ${Machine_Names[$j]} ****\n"

        #cmd="ping -I $source_ip -c 8 -w 10 $target_ip"
        cmd="ping -c 8 -w 10 $target_ip"
        ssh $ops $source_name $cmd
    done
done
