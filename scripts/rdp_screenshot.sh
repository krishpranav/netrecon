#!/bin/bash
if [ -z $1 ]; then
    echo "Usage: $0 target.ip"
    exit 1
fi

output="output"
timeout=60
timeoutStep=2
host=$1
port=$2
blue="\e[34m[*]\e[0m"
red="\e[31m[*]\e[0m"
green="\e[32m[*]\e[0m"
temp="/tmp/${host}.png"

export XAUTHORITY="$XDG_CACHE_HOME/Xauthority"

function screenshot {
    screenshot=$1
    window=$2
    import -window ${window} "${screenshot}"
}

function isAlive {
    pid=$1
    kill -0 $pid 2>/dev/null
    if [ $? -eq 1 ]; then
        exit 1
    fi
}

function isTimedOut {
    t=$1
    if [ $t -ge $timeout ]; then
        kill $!
        exit 1
    fi
}

export DISPLAY=:1

# Launch rdesktop in the background
rdesktop -u "" -a 16 $host &
pid=$!

# Get window id
window=
timer=0
    while true; do
    # Check to see if we timed out
    isTimedOut $(printf "%.0f" $timer)

   # Check to see if the process is still alive
    isAlive $pid
    window=$(xdotool search --name ${host})
    if [ ! "${window}" = "" ]; then
        break
    fi
    timer=$(echo "$timer + 0.1" | bc)
    sleep 0.1
done

# If the screen is all black delay timeoutStep seconds
timer=0
while true; do

    # Make sure the process didn't die
    isAlive $pid

    isTimedOut $timer

    # Screenshot the window and if the only one color is returned (black), give it chance to finish loading
    screenshot "${temp}" "${window}"
    colors=$(convert "${temp}" -colors 5 -unique-colors txt:- | grep -v ImageMagick)
    if [ $(echo "${colors}" | wc -l) -eq 1 ]; then
        sleep $timeoutStep
    else
        # Many colors should mean we've got a console loaded
        break
    fi
    timer=$((timer + timeoutStep))
done


if [ ! -d "${output}" ]; then
    mkdir "${output}"
fi

afterScreenshot="${output}/${host}.png"
screenshot "${afterScreenshot}" "${window}"

# run ocr on saved image(s)
base64 ${temp}

rm ${temp}

# Close the rdesktop window
kill $pid
