"""
ytdlmusic scripts
"""

import sys
import re
import os.path
import subprocess
from shutil import which


def ytdlmusic():
    """
    entry point from ytdlmusic
    """
    try:
        # special entries
        if len(sys.argv) == 1:
            display_help()
        elif len(sys.argv) == 2:
            if sys.argv[1] == "--help":
                display_help()
                sys.exit(0)

            if sys.argv[1] == "--update":
                update()
                sys.exit(0)

            if sys.argv[1] == "--full-update":
                fullupdate()
                sys.exit(0)

            if sys.argv[1] == "--version":
                version()
                sys.exit(0)

            if sys.argv[1].startswith("--"):
                print_bad_launch()
                sys.exit(1)

            print_bad_launch()
            sys.exit(1)

        elif len(sys.argv) == 3:
            if sys.argv[1].startswith("--") or sys.argv[2].startswith(
                "--"
            ):
                print_bad_launch()
                sys.exit(1)
            else:
                job(sys.argv[1], sys.argv[2], False)
                sys.exit(0)
        elif len(sys.argv) == 4:
            if not sys.argv[1].startswith("--auto"):
                print_bad_launch()
                sys.exit(1)
            else:
                job(sys.argv[2], sys.argv[3], True)
                sys.exit(0)
        else:
            print_bad_launch()
            sys.exit(1)
    except Exception as err:
        print_error(err)
        sys.exit(1)


def job(artist, song, auto):
    """
    use case
    """
    try:
        r_search = search(artist, song)
        answer = choice(r_search, auto)
        file_name = determine_filename(artist, song)
        u_choice = r_search.result()["result"][answer - 1]
        download_song(
            u_choice["link"],
            file_name,
        )
    except Exception as err:
        print_error(err)
        sys.exit(1)


def print_bad_launch():
    """
    print bad launch
    """
    print("bad parameters for ytdlmusic")
    print("ytdlmusic --help for more information")


def print_error(err):
    """
    print generic error
    """
    print("Unexpected error:", err)

    version()
    print(
        "try to upgrade with 'ytdlmusic update' or manually and retry."
    )
    print(
        "if you reproduce the error after the update : you can open an issue at https://github.com/thib1984/ytdlmusic/issues with this log"
    )


def print_error_update(err):
    """
    print generic error
    """
    print(
        "Error during the update : the update will could be finished at the restart of ytdlmusic",
        err,
    )

    print(
        "Retest the update a second time. If you reproduce the error : you can open an issue at https://github.com/thib1984/ytdlmusic/issues with this log"
    )


def version():
    """
    print version
    """
    import pkg_resources

    try:
        ytdlmusicversion = pkg_resources.get_distribution(
            "ytdlmusic"
        ).version
    except Exception:
        ytdlmusicversion = "NON INSTALLE"
    try:
        ytsearchpythonversion = pkg_resources.get_distribution(
            "youtube-search-python"
        ).version
    except Exception:
        ytsearchpythonversion = "NON INSTALLE"
    try:
        youtubedlversion = pkg_resources.get_distribution(
            "youtube-dl"
        ).version
    except Exception:
        youtubedlversion = "NON INSTALLE"
    try:
        pipversion = pkg_resources.get_distribution("pip3").version
    except Exception:
        try:
            pipversion = pkg_resources.get_distribution("pip").version
        except Exception:
            pipversion = "NON INSTALLE"
    try:
        pythonversion = "".join(sys.version.splitlines())
    except Exception:
        pythonversion = "NON INSTALLE"
    if which("ffmpeg") is None:
        ffmpeg_binary = "NON INSTALLE"
    else:
        ffmpeg_binary = which("ffmpeg")
    print("ytdlmusic version             : " + ytdlmusicversion)
    print("youtube-search-python version : " + ytsearchpythonversion)
    print("youtube-dl version            : " + youtubedlversion)
    print("pip(3) version                : " + pipversion)
    print("python version                : " + pythonversion)
    print("ffmpeg                        : " + ffmpeg_binary)


def determine_filename(artist, song):
    """
    correct filename to escape special characters
    """
    file_name = re.sub(
        "(\\W+)", "_", artist.lower() + "_" + song.lower()
    )
    if which("ffmpeg") is None:
        ext = ".ogg"
    else:
        ext = ".mp3"
    if os.path.exists(file_name + ext):
        i = 0
        while True:
            i = i + 1
            file_name_tmp = file_name + "_" + str(i)
            if not os.path.exists(file_name_tmp + ext):
                file_name = file_name_tmp
                break
    print("future filename is : " + file_name + ext)
    return file_name


def search(artist, song):
    """
    search the items
    """
    from youtubesearchpython import VideosSearch

    print("artist : " + artist)
    print("song : " + song)
    print(
        "search "
        + artist
        + " "
        + song
        + " mp3 with youtubesearchpython"
    )
    results_search = VideosSearch(
        artist + " " + song + " mp3", limit=5
    )

    return results_search


def choice(results_search, auto):
    """
    user choice
    """
    i = 0
    if len(results_search.result()["result"]) == 0:
        print("no result, retry with other words")
        sys.exit(0)
    answer = 1
    if not auto:
        for children in results_search.result()["result"]:
            i = i + 1
            print(i)
            print(children["title"])
            print(children["link"])
            print(
                children["duration"]
                + " - "
                + children["viewCount"]["text"]
            )

        while True:
            answer = input(
                "which (1-"
                + str(len(results_search.result()["result"]))
                + ", 0 to exit properly) ? "
            )
            if (
                answer.isnumeric()
                and int(answer) >= 0
                and int(answer) <= 5
            ):
                break
        if int(answer) == 0:
            sys.exit(0)
    return int(answer)


def download_song(song_url, song_title):
    """
    download song in song_title.mp3/ogg format with youtube_dl from url song_url
    """
    import youtube_dl

    print("download " + song_url + " with youtubedl")
    if which("ffmpeg") is None:
        ext = ".ogg"
        outtmpl = song_title + ".ogg"
        ydl_opts = {"format": "bestaudio/best", "outtmpl": outtmpl}
    else:
        ext = ".mp3"
        outtmpl = song_title + ".%(ext)s"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {"key": "FFmpegMetadata"},
            ],
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(song_url, download=True)
    if which("ffmpeg") is None:
        print(
            "warning : ogg was used. If you want mp3 format, install ffmpeg fo your system."
        )
    print(song_title + ext + " is ready")


def display_help():
    """
    help
    """
    help_txt = """\

    NAME
        ytdlmusic

    SYNOPSIS
       With ytdlmusic, you can download from youtube a mp3 or ogg music without use browser. 5 choices are available with small summary 
       to facilitate the choice. You can also use auto mode to download the first item. 

        --help              : display this help
                            -> ytdlmusic --help
        --update            : upgrade ytdlmusic
                            -> ytdlmusic --update   
        --full-update       : upgrade youtube-dl, youtube-search-python and ytdlmusic
                            -> ytdlmusic --full-update                                                   
        --version           : display versions of ytdlmusic and his dependencies
                            -> ytdlmusic --version                         
        artist song         : display 5 choices from youtube with given search, then download the mp3 or ogg choosen by user
                            -> example : ytdlmusic "the beatles" "let it be"
        --auto artist song  : download mp3 or ogg of the first from youtube with given search
                            -> example : ytdlmusic --auto "the beatles" "let it be"
        """
    print(help_txt)


def update():
    """
    update
    """
    while True:
        answer = input("update the ytdlmusic package [y/n] ? ")
        if answer == "y":
            break
        if answer == "n":
            sys.exit(0)
    try:
        prog = "pip3"
        if which(prog) is None:
            prog = "pip"
        update_ytdlmusic(prog)
    except Exception as err:
        print_error_update(err)


def fullupdate():
    """
    fullupdate
    """
    while True:
        answer = input(
            "update the ytdlmusic package and the dependencies [y/n] ? "
        )
        if answer == "y":
            break
        if answer == "n":
            sys.exit(0)
    try:
        prog = "pip3"
        if which(prog) is None:
            prog = "pip"
        update_ytdlmusic(prog)
        update_dependencies(prog)
    except Exception as err:
        print_error_update(err)


def update_dependencies(prog):
    """
    update of dependencies
    """
    print("try to update youtube-search-python with " + prog)
    subprocess.check_call(
        [
            prog,
            "install",
            "--upgrade",
            "youtube-search-python",
        ]
    )
    print("try to update youtube-dl with " + prog)
    subprocess.check_call(
        [
            prog,
            "install",
            "--upgrade",
            "youtube-dl",
        ]
    )


def update_ytdlmusic(prog):
    """
    update of ytdlmusic
    """
    print("try to update ytdlmusic with " + prog)
    subprocess.check_call(
        [
            prog,
            "install",
            "--upgrade",
            "ytdlmusic",
        ]
    )


if __name__ == "__main__":
    ytdlmusic()
