"""
games/diff_data.py — 30 paires d'images (10 par match)
Format fichiers : 1.Left.jpeg / 1.Right.jpeg ... 30.Left.jpeg / 30.Right.jpeg
"""

ALL_DIFFS = [
{"left": "31.Left.jpeg",  "right": "31.Right.jpeg",  "title": "Image 1", "diffs": [(380, 412, 40), (586, 333, 40), (363, 277, 40), (48, 273, 40), (573, 241, 40)]},
{"left": "2.Left.jpeg",  "right": "2.Right.jpeg",  "title": "Image 2", "diffs": [(83, 387, 40), (494, 309, 40), (283, 268, 40), (578, 143, 40), (184, 141, 40)]},
{"left": "3.Left.jpeg",  "right": "3.Right.jpeg",  "title": "Image 3", "diffs": [(374, 438, 40), (82, 392, 40), (516, 310, 40), (518, 162, 40), (278, 101, 40)]},
{"left": "4.Left.jpeg",  "right": "4.Right.jpeg",  "title": "Image 4", "diffs": [(128, 437, 40), (581, 434, 40), (244, 247, 40), (557, 189, 40), (471, 38, 40)]},
{"left": "5.Left.jpeg",  "right": "5.Right.jpeg",  "title": "Image 5", "diffs": [(235, 433, 40), (227, 277, 40), (393, 202, 40), (573, 64, 40), (186, 25, 40)]},
{"left": "6.Left.jpeg",  "right": "6.Right.jpeg",  "title": "Image 6", "diffs": [(497, 386, 40), (283, 248, 40), (35, 150, 40), (412, 84, 40), (525, 52, 40)]},
{"left": "7.Left.jpeg",  "right": "7.Right.jpeg",  "title": "Image 7", "diffs": [(170, 275, 40), (373, 232, 40), (520, 250, 40), (193, 211, 40), (595, 155, 40)]},
{"left": "8.Left.jpeg",  "right": "8.Right.jpeg",  "title": "Image 8", "diffs": [(131, 404, 40), (345, 269, 40), (83, 208, 40), (444, 149, 40), (314, 151, 40)]},
{"left": "9.Left.jpeg",  "right": "9.Right.jpeg",  "title": "Image 9", "diffs": [(564, 392, 40), (55, 287, 40), (577, 255, 40), (241, 154, 40), (376, 23, 40)]},
{"left": "10.Left.jpeg",  "right": "10.Right.jpeg",  "title": "Image 10", "diffs": [(160, 433, 40), (460, 431, 40), (140, 300, 40), (68, 88, 40), (541, 80, 40)]},
{"left": "11.Left.jpeg",  "right": "11.Right.jpeg",  "title": "Image 11", "diffs": [(326, 288, 40), (529, 283, 40), (55, 256, 40), (262, 157, 40), (70, 60, 40)]},
{"left": "12.Left.jpeg",  "right": "12.Right.jpeg",  "title": "Image 12", "diffs": [(82, 421, 40), (69, 336, 40), (401, 333, 40), (309, 135, 40), (588, 40, 40)]},
{"left": "13.Left.jpeg",  "right": "13.Right.jpeg",  "title": "Image 13", "diffs": [(412, 408, 40), (536, 333, 40), (145, 298, 40), (597, 128, 40), (75, 66, 40)]},
{"left": "14.Left.jpeg",  "right": "14.Right.jpeg",  "title": "Image 14", "diffs": [(118, 410, 40), (354, 363, 40), (198, 137, 40), (527, 44, 40), (71, 44, 40)]},
{"left": "15.Left.jpeg",  "right": "15.Right.jpeg",  "title": "Image 15", "diffs": [(86, 399, 40), (226, 353, 40), (130, 261, 40), (447, 206, 40), (560, 193, 40)]},
{"left": "16.Left.jpeg",  "right": "16.Right.jpeg",  "title": "Image 16", "diffs": [(218, 343, 40), (591, 236, 40), (441, 150, 40), (356, 50, 40), (78, 69, 40)]},
{"left": "17.Left.jpeg",  "right": "17.Right.jpeg",  "title": "Image 17", "diffs": [(42, 433, 40), (277, 424, 40), (263, 297, 40), (90, 78, 40), (338, 30, 40)]},
{"left": "18.Left.jpeg",  "right": "18.Right.jpeg",  "title": "Image 18", "diffs": [(410, 396, 40), (39, 381, 40), (67, 271, 40), (561, 203, 40), (46, 170, 40)]},
{"left": "19.Left.jpeg",  "right": "19.Right.jpeg",  "title": "Image 19", "diffs": [(596, 381, 40), (433, 271, 40), (439, 204, 40), (345, 158, 40), (462, 69, 40)]},
{"left": "20.Left.jpeg",  "right": "20.Right.jpeg",  "title": "Image 20", "diffs": [(595, 383, 40), (509, 374, 40), (287, 318, 40), (573, 245, 40), (263, 39, 40)]},
{"left": "21.Left.jpeg",  "right": "21.Right.jpeg",  "title": "Image 21", "diffs": [(595, 261, 40), (500, 264, 40), (133, 266, 40), (77, 134, 40), (318, 85, 40)]},
{"left": "22.Left.jpeg",  "right": "22.Right.jpeg",  "title": "Image 22", "diffs": [(480, 428, 40), (79, 360, 40), (566, 242, 40), (234, 173, 40), (416, 66, 40)]},
{"left": "23.Left.jpeg",  "right": "23.Right.jpeg",  "title": "Image 23", "diffs": [(547, 386, 40), (77, 219, 40), (190, 208, 40), (356, 145, 40), (548, 36, 40)]},
{"left": "24.Left.jpeg",  "right": "24.Right.jpeg",  "title": "Image 24", "diffs": [(569, 359, 40), (264, 330, 40), (564, 220, 40), (574, 104, 40), (134, 78, 40)]},
{"left": "25.Left.jpeg",  "right": "25.Right.jpeg",  "title": "Image 25", "diffs": [(550, 380, 40), (37, 377, 40), (76, 277, 40), (290, 112, 40), (452, 39, 40)]},
{"left": "26.Left.jpeg",  "right": "26.Right.jpeg",  "title": "Image 26", "diffs": [(315, 365, 40), (126, 329, 40), (37, 319, 40), (375, 288, 40), (306, 153, 40)]},
{"left": "27.Left.jpeg",  "right": "27.Right.jpeg",  "title": "Image 27", "diffs": [(572, 419, 40), (184, 397, 40), (504, 214, 40), (367, 208, 40), (77, 44, 40)]},
{"left": "28.Left.jpeg",  "right": "28.Right.jpeg",  "title": "Image 28", "diffs": [(557, 424, 40), (401, 247, 40), (88, 230, 40), (543, 209, 40), (434, 34, 40)]},
{"left": "29.Left.jpeg",  "right": "29.Right.jpeg",  "title": "Image 29", "diffs": [(283, 435, 40), (579, 319, 40), (272, 268, 40), (495, 129, 40), (384, 51, 40)]},
{"left": "30.Left.jpeg",  "right": "30.Right.jpeg",  "title": "Image 30", "diffs": [(228, 331, 40), (317, 354, 40), (471, 355, 40), (233, 202, 40), (30, 29, 40)]}




]