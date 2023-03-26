from speech_synthesis import downloadListStories, combileAduio
from drawIMG import drawIMG
from scrawl_stories import scrawl_stories


def main():
    chapter_start = 16
    chapter_count = 30
    chapter_combine = 3
    # scrawl_stories(chapter_start=chapter_start, chapter_counts=chapter_count)
    # downloadListStories()
    combileAduio(combine_count=chapter_combine)
    drawIMG(img_start=chapter_start, img_step=chapter_combine)


if __name__ == '__main__':
    main()
