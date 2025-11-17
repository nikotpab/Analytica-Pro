import sys

print('Bienvenidx a discretización Chi-Merge')
fill = input('Ingrese  el número de datos que desea normalizar:\n')
nombClass = input('Ingrese  el nombre de la clases separados por coma (por ejemplo: A,B):\n')

num_intervals_deseados1 = 3
num_intervals_deseados2 = 3

print('Ingrese los datos en este formato:')
print('X,Y,CLASE (separados por coma)')

bigList = []
parts = nombClass.strip().split(',')

for i in range(int(fill)):
    data = input('Ingrese el registro número {}\n'.format(i + 1)).replace(' ', '').split(',')

    classs = str(data[2])
    if classs not in parts:
        print(f'La clase {classs} no es válida.')
        sys.exit()

    smallList = [data[0], data[1], data[2]]
    bigList.append(smallList)

dataSet1 = []
dataSet2 = []

for i in range(int(fill)):
    smallList1 = [(bigList[i][0], bigList[i][2])]
    dataSet1.append(smallList1)

for i in range(int(fill)):
    smallList2 = [(bigList[i][1], bigList[i][2])]
    dataSet2.append(smallList2)

print('DataSet 1:')
print(dataSet1)
print('DataSet 2:')
print(dataSet2)

intervals = []
previous_inter = 0

for i in range(len(dataSet1)):
    inter = 0

    if (i == len(dataSet1) - 1):
        start_val = previous_inter
        end_val = int(dataSet1[i][0][0]) + 1
        str_inter = str('[{},{}]'.format(start_val, end_val))
        intervals.append(str_inter)
        break

    x1 = int(dataSet1[i][0][0])
    x2 = int(dataSet1[i + 1][0][0])
    inter = int((x1 + x2) / 2)

    if (i == 0):
        str_inter = str('[0,{}]'.format(inter))
        intervals.append(str_inter)
        previous_inter = inter
    else:
        str_inter = str('[{},{}]'.format(previous_inter, inter))
        intervals.append(str_inter)
        previous_inter = inter

print('Intervalos DataSet 1:')
print(intervals)

intervals2 = []
previous_inter = 0
for i in range(len(dataSet2)):
    inter = 0

    if (i == len(dataSet2) - 1):
        start_val = previous_inter
        end_val = int(dataSet2[i][0][0]) + 1
        str_inter = str('[{},{}]'.format(start_val, end_val))
        intervals2.append(str_inter)
        break

    x1 = int(dataSet2[i][0][0])
    x2 = int(dataSet2[i + 1][0][0])
    inter = int((x1 + x2) / 2)

    if (i == 0):
        str_inter = str('[0,{}]'.format(inter))
        intervals2.append(str_inter)
        previous_inter = inter
    else:
        str_inter = str('[{},{}]'.format(previous_inter, inter))
        intervals2.append(str_inter)
        previous_inter = inter

print('Intervalos DataSet 2:')
print(intervals2)

while len(intervals) > num_intervals_deseados1:
    chi_squ = []

    for i in range(len(dataSet1) - 1):

        int1_data = dataSet1[i]
        int2_data = dataSet1[i + 1]

        A1 = sum(1 for item in int1_data if item[1] == parts[0])
        B1 = sum(1 for item in int1_data if item[1] == parts[1])
        A2 = sum(1 for item in int2_data if item[1] == parts[0])
        B2 = sum(1 for item in int2_data if item[1] == parts[1])

        sum_row1 = A1 + B1
        sum_row2 = A2 + B2

        Suma_ColA = A1 + A2
        Suma_ColB = B1 + B2

        tot = sum_row1 + sum_row2

        if tot == 0:
            chi_squ.append(0)
            continue

        E11 = (sum_row1 * Suma_ColA) / tot
        E12 = (sum_row1 * Suma_ColB) / tot
        E21 = (sum_row2 * Suma_ColA) / tot
        E22 = (sum_row2 * Suma_ColB) / tot

        chi_sq = 0.0

        if E11 > 0:
            chi_sq += ((A1 - E11) ** 2) / E11
        if E12 > 0:
            chi_sq += ((B1 - E12) ** 2) / E12
        if E21 > 0:
            chi_sq += ((A2 - E21) ** 2) / E21
        if E22 > 0:
            chi_sq += ((B2 - E22) ** 2) / E22

        chi_squ.append(chi_sq)

    if not chi_squ:
        break

    min_chi = min(chi_squ)
    min_index = chi_squ.index(min_chi)

    dataSet1[min_index] = dataSet1[min_index] + dataSet1[min_index + 1]
    del dataSet1[min_index + 1]

    interval1_str = intervals[min_index]
    interval2_str = intervals[min_index + 1]

    start_val = interval1_str.split(',')[0].replace('[', '')
    end_val = interval2_str.split(',')[1].replace(']', '')

    intervals[min_index] = f"[{start_val},{end_val}]"
    del intervals[min_index + 1]

while len(intervals2) > num_intervals_deseados2:
    chi_squ2 = []

    for i in range(len(dataSet2) - 1):

        int1_data = dataSet2[i]
        int2_data = dataSet2[i + 1]

        A1 = sum(1 for item in int1_data if item[1] == parts[0])
        B1 = sum(1 for item in int1_data if item[1] == parts[1])
        A2 = sum(1 for item in int2_data if item[1] == parts[0])
        B2 = sum(1 for item in int2_data if item[1] == parts[1])

        sum_row1 = A1 + B1
        sum_row2 = A2 + B2

        Suma_ColA = A1 + A2
        Suma_ColB = B1 + B2

        tot = sum_row1 + sum_row2

        if tot == 0:
            chi_squ2.append(0)
            continue

        E11 = (sum_row1 * Suma_ColA) / tot
        E12 = (sum_row1 * Suma_ColB) / tot
        E21 = (sum_row2 * Suma_ColA) / tot
        E22 = (sum_row2 * Suma_ColB) / tot

        chi_sq = 0.0

        if E11 > 0:
            chi_sq += ((A1 - E11) ** 2) / E11
        if E12 > 0:
            chi_sq += ((B1 - E12) ** 2) / E12
        if E21 > 0:
            chi_sq += ((A2 - E21) ** 2) / E21
        if E22 > 0:
            chi_sq += ((B2 - E22) ** 2) / E22

        chi_squ2.append(chi_sq)

    if not chi_squ2:
        break

    min_chi = min(chi_squ2)
    min_index = chi_squ2.index(min_chi)

    dataSet2[min_index] = dataSet2[min_index] + dataSet2[min_index + 1]
    del dataSet2[min_index + 1]

    interval1_str = intervals2[min_index]
    interval2_str = intervals2[min_index + 1]

    start_val = interval1_str.split(',')[0].replace('[', '')
    end_val = interval2_str.split(',')[1].replace(']', '')

    intervals2[min_index] = f"[{start_val},{end_val}]"
    del intervals2[min_index + 1]

print('\nRESULTADO FINAL:')
print('\nIntervalos del DataSet 1:')
print(intervals)
print('Datos agrupados del DataSet 1:')
print(dataSet1)
print('\nIntervalos del DataSet 2:')
print(intervals2)
print('Datos agrupados DataSet 2:')
print(dataSet2)