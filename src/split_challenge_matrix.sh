#!/bin/bash


INPUT=$1

if [ -z "$INPUT" ]; then
    echo "Usage: $0 <challenge_matrix_file>"
    exit 1
fi

NAME=$(basename $INPUT .csv)
echo $NAME


SPLIT1="$NAME.__15m.csv"
SPLIT2="$NAME.15m_1h.csv"
SPLIT3="$NAME.1h_4h.csv"
SPLIT4="$NAME.4h__.csv"

HEADER=$(head -1 $INPUT)
echo $HEADER > $SPLIT1
echo $HEADER > $SPLIT2
echo $HEADER > $SPLIT3
echo $HEADER > $SPLIT4

rg "<15 min fix" $INPUT >> $SPLIT1
rg "15 min - 1 hour" $INPUT >> $SPLIT2
rg "1-4 hours" $INPUT >> $SPLIT3
rg ">4 hours" $INPUT >> $SPLIT4

echo "Created files:"
echo "$SPLIT1"
echo "$SPLIT2"
echo "$SPLIT3"
echo "$SPLIT4"