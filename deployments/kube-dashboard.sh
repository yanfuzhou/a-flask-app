#!/bin/bash
USER_KUBE_DASHBOARD=${HOME}/.${USER}-kube-dashboard.pid

function quit() {
    if test -f ${USER_KUBE_DASHBOARD}; then
        kill -9 $(head -n 1 ${USER_KUBE_DASHBOARD})
        rm -f ${USER_KUBE_DASHBOARD}
    fi
}

case "$1" in
    start)
        quit
        kubectl proxy &>/dev/null & echo $! > ${USER_KUBE_DASHBOARD}
        ;;         
    stop)
        quit
        ;;
    restart)
        start
        ;;         
    *)
        echo $"Usage: $0 {start|stop|restart}"
        exit 1
esac