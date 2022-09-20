# Description
Reads two given html source codes into BeautifulSoup objects. Extracts features and predicts whether one html source code is a phishing attempt masquerading as the other.

Current extracted features,
1) a_no_ratio:
Comparison of anchor tag href attribute counts.

2) img_src_ratio:
Comparison of identical image file names found in img tag src attribute.

3) link_href_ratio:
Comparison of identical external resource file names found in link tag href attribute.

4) link_href_count:
Count of identical external resource file names found in link tag href attribute.

5) div_class_ratio:
Comparison of identical style class names found in div tag class attribute.

6) div_class_count:
Count of identical style class names found in div tag class attribute.

7) overall_word_ratio:
Comparison of identical words found in title, h1 to h6, and p tag contents, as well as meta tag content attribute.

8) overall_word_count:
Count of identical words found in title, h1 to h6, and p tag contents, as well as meta tag content attribute.

9) meta_content_ratio:
Comparison of meta information found in meta tag content attribute.

10) filtered_word_ratio:
Same as overall_word_ratio, but filtered for words of >2 letters that begin with a capital letter or 'http'.

11) filtered_word_count:
Same as overall_word_count, but filtered for words of >2 letters that begin with a capital letter or 'http'.

12) word_length_list:
Relative length of filtered word lists.

# How to Use
Navigate to relevant iteration in the 'iterations' directory and run main.py.

Type in terminal,

```
python3 iterations/'number'/main.py --html1 'html1_path' --html2 'html2_path'
```

Where 'html1_path' and 'html2_path' are file paths to two html source codes to be compared against each other.

Example,

```
python3 iterations/2/main.py --html1 phish_test/original.html --html2 phish_test/phish.html
```
