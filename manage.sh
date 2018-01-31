#!/bin/sh


if [ $# -lt 2 ];then
    action="$1"
    name="service"
elif [ $# -lt 3 ];then
    action="$1"
    name="$2"
else
    echo "Usage:${0} start|stop|restart|reload"
    exit 0;
fi

PROJECT_DIR=`cd $(dirname "$0");pwd`

cd ${PROJECT_DIR}

config_file="${PROJECT_DIR}/config.ini"
echo $config_file

# if ./logs dir is not exist, mkdir ./logs
[ ! -d "${PROJECT_DIR}/logs" ] && mkdir -p ${PROJECT_DIR}/logs

pid_exists () {
    # This is better than "kill -0" because it doesn't require permission to
    # send a signal (so daemon_status in particular works as non-root).
    test -d /proc/"$1"
}

daemon_is_running () {
    proc=$1
    proc_pids=$(pgrep -f "${proc}")
    test -z ${proc_pids} && return 1
    for pid in ${proc_pids}
    do
        test -n "${pid}" && pid_exists "${pid}"
    done
} > /dev/null 2>&1

daemon_start_server() {
    if daemon_is_running "${config_file}"; then
        echo "Server is already running."
    else
        uwsgi --ini ${config_file} > /dev/null 2>&1
        echo "Server started."
    fi
}

daemon_stop_server() {
    if daemon_is_running "${config_file}"; then
        ps -ef | grep "${config_file}" | grep "uwsgi" | grep -v grep | awk '{print $2}' | xargs kill -9
        sleep 1
        echo "Server stopped."
    else
        echo "Server is not running."
    fi
}

daemon_reload_server() {
    uwsgi --reload ${PROJECT_DIR}/run/runapp.pid
    sleep 1
    echo "Server reloaded."
}

daemon_start_celery() {
    if daemon_is_running "celery worker"; then
        echo "Celery is already running."
    else
        nohup celery worker -l DEBUG -A application.celery --logfile logs/celery_worker.log > /dev/null 2>&1 &
        daemonpid=$!
        sleep 1
        if kill -0 $daemonpid ; then
            echo "Celery started."
        else
            echo "Celery start failure."
        fi
    fi
}

daemon_stop_celery() {
    if daemon_is_running "celery worker"; then
        ps -ef | grep "celery worker" | grep -v grep | awk '{print $2}' | xargs kill -9
        sleep 1
        echo "Celery stopped."
    else
        echo "Celery is not running."
    fi
}

case "${action}" in
    start)
        if [ X"${name}" == X"all" ]
        then
            daemon_start_server
            sleep 1
            daemon_start_celery
        elif [ X"${name}" == X"celery" ]
        then
            daemon_start_celery
        else
            daemon_start_server
        fi
    ;;
    stop)
        if [ X"${name}" == X"all" ]
        then
            daemon_stop_server
            sleep 1
            daemon_stop_celery
        elif [ X"${name}" == X"celery" ]
        then
            daemon_stop_celery
        else
            daemon_stop_server
        fi
    ;;
    restart)
        if [ X"${name}" == X"all" ]
        then
            daemon_stop_server
            sleep 1
            daemon_start_server
            sleep 1
            daemon_stop_celery
            sleep 1
            daemon_start_celery
        elif [ X"${name}" == X"celery" ]
        then
            daemon_stop_celery
            sleep 1
            daemon_start_celery
        else
            daemon_stop_server
            sleep 1
            daemon_start_server
        fi
    ;;
    reload)
        if [ X"${name}" != X"service" ]
        then
            echo "not support to reload ${name}!!!"
            exit 1;
        fi
        daemon_reload_server
    ;;
    *)
        echo "Usage: sh $(basename "$0") {start|stop|restart|reload}"
        exit 1
esac
exit 0
