for d in $(ls .); do
  if [ -d $d ]; then
    echo "clean" $d
    ls $d/* | grep -v $d.txt | grep -v $d.wav | xargs rm -f
  fi
done