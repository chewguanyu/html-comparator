# Description
Reads two given html source codes into BeautifulSoup objects. Extracts features and predicts whether one html source code is a phishing attempt on the other.

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

7) word_ratio:
Comparison of identical words found in p tag.

8) word_count:
Count of identical words found in p tag.

9) meta_content_ratio:
Comparison of meta information found in meta tag content attribute.
