#!/bin/bash
# today shell
#
# render date, day info based in cityCode of Brasil
# 
tname=$(date "+%d%m%y.md")
tfile="lab/daylog/$tname"
# 244 = sao paulo
cityCode=244


for i in "$@"
do
case $i in
    -e|--edit)
    EDIT="${i#*=}"

    ;;
esac

case $i in
    -i|--insert)
    INSERT="${i#*=}"

    ;;
esac
case $i in
    -s|--short|-short)
    SHORT="${i#*=}"

    ;;
esac
case $i in
    -n|--new|-new)
    NEW="${i#*=}"

    ;;
esac
case $i in
    -drop|--delete|-del)
    DELETE="${i#*=}"

    ;;
esac
case $i in
    -a|--add|-add)
    ADD="${i#*=}"

    ;;
esac
case $i in
    -ok|--done|-done)
    CHECKED="${i#*=}"

    ;;
esac
case $i in
    -day|--day)
    DAYSEARCH="${i#*=}"

    ;;
esac

case $i in
    -fail|--undone|-undone)
    UNCHECKED="${i#*=}"

    ;;
esac
done

removeTask()
{
    id=$1
    if [ -z $id ]; then
        echo "erro, you need id to change"
    else
        echo "remove task $id"
        deletedFile="/tmp/removed-$id-task.md"
        sed /$id\ \-/d $tfile > $deletedFile
        rm $tfile
        mv $deletedFile $tfile
        glow $tfile
    fi
}

updateState()
{
    id=$1
    if [ -z $1 ]; then
        echo "erro, you need id to change"
    elif [ -z $2 ]; then
        echo "erro, you need status to change"
    elif $2 ; then
        filterTodo="- \[ \] $id - "
        checkedTodo="- \[x\] $id - "
        cat $tfile | sed -e  "s/$filterTodo/$checkedTodo/g" > '/tmp/file.md'
        rm $tfile
        mv /tmp/file.md $tfile
        glow $tfile
    else
        filterTodo="- \[x\] $id - "
        checkedTodo="- \[ \] $id - "
        cat $tfile | sed -e  "s/$filterTodo/$checkedTodo/g" > '/tmp/file.md'
        rm $tfile
        mv /tmp/file.md $tfile
        glow $tfile
    fi
}


parseClima()
{ 
    pathJson=$1
    cidade=$(cat $pathJson | jq ".cidade")
    min=$(cat  $pathJson | jq ".clima[0].min")
    max=$(cat  $pathJson | jq ".clima[0].max")
    cond=$(cat $pathJson | jq ".clima[0].condicao_desc")
    dt=$(date "+ %d/%m/%y")
    dweek=$(date "+ %A")
printf "# Diario - $dt
\n\n
- $dweek - $cidade - max: $max ºC min: $min ºC 
\n
- Condições: $cond
\n\n\n
## TODO
\n\n"
}


newDay()
{
    pathJson="/tmp/clima.json"
    curl https://brasilapi.com.br/api/cptec/v1/clima/previsao/$cityCode > $pathJson
    parseClima $pathJson > $tfile    
    glow $tfile
}

printName()
{
  figlet today cli
}

if [ "$INSERT" ]; then
    nvim "$tfile"
elif [ "$NEW" ]; then
    newDay
elif [ "$DAYSEARCH" ]; then
    if [ -z $2 ]; then
        echo "you need pass day back to read file"
    else
        fileResult=$(date -v -$2d "+%d%m%y.md")
        glow "lab/daylog/$fileResult"
    fi
elif [ "$DELETE" ]; then
    removeTask $2
elif [ "$ADD" ]; then
    echo "add new item in todo"
    hashId=$(echo $2 | openssl sha512 | cut -d'=' -f2 | cut -c 2-5)
    echo " - [ ] $hashId - $2" >> $tfile
elif [ "$EDIT" ]; then
    if [ -z $2 ]; then
        echo "erro, you need id of task"
    else
        echo "WIP - not implement yet"
    fi
elif [ "$CHECKED" ]; then
   echo "done item - $2"
   updateState $2 true
elif [ "$UNCHECKED" ]; then
   echo "not done item - $2"
   updateState $2 false
elif [ "$SHORT" ]; then
    printName
    glow $tfile
else
    printName
    if [ -e $tfile ]
    then
        cal && glow $tfile
    else
        echo -n "generate new day? yes or not (y, N): "
        read response
        if [[ "$response" == "y" ]]; then
            echo "starting generating.."
            echo "good day for you!!"
            newDay
        fi
    fi
fi

