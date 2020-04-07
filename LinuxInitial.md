1. screen - написать конфиг файл для него что б были видны окна, например:

    ```
    hardstatus alwayslastline
    hardstatus string '%{= G}[ %{G}%H %{g}][%= %{= G}%-w%{y} %n*%t%?(%u)%? %{-}%+w %=%{G}][ %{Y}Load: %l %{g}][%{B}%d-%m-%Y %{W}%c:%s %{g}]'
    defscrollback 5000
    startup_message off
    attrcolor b ".I"
    termcapinfo xterm 'Co#256:AB=\E[48;5;%dm:AF=\E[38;5;%dm'
    defbce on
    screen -t bash 1 bash
    select 0
    bind s split
    ```
2. умение пользоваться пайпом и стандартным набором команд
    Пример
    `netstat -na` выведет тебе список всех открыхых портов:
    пример:
    ```
    tcp46      0      0  *.3000                 *.*                    LISTEN     
    tcp4       0      0  127.0.0.1.63342        *.*                    LISTEN     
    tcp4       0      0  127.0.0.1.6942         *.*                    LISTEN
    ```
Можеш выпарсить только порты из этого вывода? Типа такого:
    ```
    3000
    63342
    6942
    49937
    49923
    49329
    27017
    ```    
    `netstat -na | grep LISTEN | awk '{print $4}' | awk '{FS=":"; print $2}' | xargs -I{} echo {}`


3. если ты запустиш top, один из параметров будет load average
что это? сколько для твоей машины максимум и почему

    load average — средняя нагрузка на систему (в целом можно считать как нагрузку на процессор, но в линуксе учитывается еще и процессы, что ждут разблокировки ресурса), судя из этого максимальное значение будет +/- значением количества ядер. к тому же выводится тремя числами за 1мин, 5мин, 15мин для прослеживания динамики
    
    так а как объяснить что происходит если у тебя load average 25 а коров только 5 ?

    тем, что большое количество задач находится в очереди

4. xargs
    1. допустим у тебя открыто сотни программ, к примеру так:
`nc -u localhost 2222
nc -u localhost 2223`

   Как мне потушить их все одной строкой ?

   xargs — использовал на
      `ls | xargs rm`

, но если вывести список через top -b, взять по условию названия программы в awk , и отфильтровать, то можно убить через xargs kill -9
    
    top -n 1 -b -u gleb | awk '{print $0}'| grep konsole | awk '{print $1}' | xargs kill -9

b) как заранить одну программу в несколько потоков с помощью xargs
    
    echo '1 1 1 1 1' | tr ' ' '\n' | xargs -I{} -n1 -P5  sleep {}
    
5. init process - что это такое, какой pid, что будет если убить?
    init process pid -- 1
6. разница между pid и ppid? что будет если убить ppid ?

    pid - process indentification number ( каждый процес запускается с уникальным, на данный момент номером), ppid - parent pid .  init process - запускает другие процессы (т.е. определенный уровень системы) (убить его не получилось, и по опыту других людей, видимо так и есть)
    
7. как сделать и подключить дополнительный swap file (используй dd для создания файла) ?
    `dd if=/dev/zero of=/mnt/swapfile bs=1024 count=2000000`
    что бы просто создать,  но потом надо еще подключить с mkswap, swapon
8. как померять скорость записи на диск?
    `sudo iotop -o`
    
    iowait коефициент загруски системы, связанный с простоем для ожидания дисковых операций, ну например у тебя 20 % wait

    диск не успевает, либо медленно отвечает
    тогда 20% процессорного времени уходит на ожидание (проверки и переключения)

    ага, а как посмотреть сколько сейчас?
    можно даже через top (пармметр wa)

9. сделать утилиту для сортировки файлов по кол-ву слов
    Пример запуска: ./sortfiles.sh /path/to/directory/with/files/

    да, надо сделать статистику количества слов в разных файлах

    Завдання з зірочкою
    сделай такое и на баше тоже)
    статистику возьми с помощью wc , запиши в файл и отсортируй записи в файле по количеству слов
    но сейчас сделаю для количества слов
    `ls | xargs -I{} wc -w {} | sort -g`

    но можно сделать так
       1. Все файлы сконкатить в один поток
      
        one two
        one two three
        
      2. Разбить их на одно слово - одна строка
            
            one
            two
            one
            two
            three
           
      3 посчитать вхождения и отсортировать

    один паровоз, если тебе нужно сохранить состояние где-то - значит делаеш что-то не так
    `ls | xargs -I{} cat {} | grep -o '[[:alpha:]]*' | sort | uniq -c | sort`


10. ffmpeg
```
gleb@gleb-HP-250-G6-Notebook-PC:~/Downloads/ffmpeg/ffmpeg-4.2.2$ ./configure
nasm/yasm not found or too old. Use --disable-x86asm for a crippled build.

If you think configure made a mistake, make sure you are using the latest
version from Git.  If the latest version fails, report the problem to the
ffmpeg-user@ffmpeg.org mailing list or IRC #ffmpeg on irc.freenode.net.
Include the log file "ffbuild/config.log" produced by configure as this will help
solve the problem.
```
==> `sudo apt install yasm` ==> `./configure` ==> `make` compiling for 30 min all packeges ==>
```
gleb@gleb-HP-250-G6-Notebook-PC:~$ ffmpeg
ffmpeg version 4.2.2 Copyright (c) 2000-2019 the FFmpeg developers
  built with gcc 7 (Ubuntu 7.4.0-1ubuntu1~18.04.1)
  configuration: 
  libavutil      56. 31.100 / 56. 31.100
  libavcodec     58. 54.100 / 58. 54.100
  libavformat    58. 29.100 / 58. 29.100
  libavdevice    58.  8.100 / 58.  8.100
  libavfilter     7. 57.100 /  7. 57.100
  libswscale      5.  5.100 /  5.  5.100
  libswresample   3.  5.100 /  3.  5.100
Hyper fast Audio and Video encoder
usage: ffmpeg [options] [[infile options] -i infile]... {[outfile options] outfile}...

Use -h to get full help or, even better, run 'man ffmpeg'
```
create gif

`ffmpeg -i input.mp4 output.gif`

creating witn loss of quality (in my case)

` ffmpeg -ss 1 -t 7 -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
`

creating with timecodes 00:01 - 00:07 infitity looped gif 


I tried to create custom build of ffmpeg
`./configure --disable-all --enable-ffmpeg --enable-small --enable-avcodec --enable-avcodec --enable-avformat --enable-protocol=file --enable-demuxer=movB --enable-swscale --enable-decoder=h264 --enable-encoder=rawvideo,libx264 --enable-avfilter`

`gleb@gleb-HP-250-G6-Notebook-PC:~/Downloads/ffmpeg/ffmpeg-4.2.2$ ls -lh ffmpeg
-rwxrwxr-x 1 gleb gleb 1,9M кві  7 21:42 ffmpeg`
