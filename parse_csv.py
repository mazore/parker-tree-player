import time
from csv import reader
import sys


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


def parse_csv(filename):
    result = []

    with open(filename, 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)

        # Iterate over each row in the csv using reader object
        lineNumber = 0
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            # break up the list of rgb values
            # remove the first item
            if lineNumber > 0:
                parsed_row = []
                row.pop(0)
                chunked_list = list(chunks(row, 3))
                for element_num in range(len(chunked_list)):
                    # this is a single light
                    r = float(chunked_list[element_num][0])
                    g = float(chunked_list[element_num][1])
                    b = float(chunked_list[element_num][2])
                    light_val = (g, r, b)
                    # turn that led on
                    parsed_row.append(light_val)

                # append that line to lightArray
                result.append(parsed_row)
            # time.sleep(0.03)

            lineNumber += 1

    return result
