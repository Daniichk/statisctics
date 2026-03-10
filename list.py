number_elements = int(input('Enter the number of elemnets:   '))
numbers = []
sum_numbers = 0
for i in range(0,number_elements):
    number = int(input('Enter number:   '))
    numbers.append(number)
# finding the medium
for i in numbers:
    sum_numbers+=i
medium = sum_numbers/len(numbers)
# finding the media
numbers_sorted = numbers.sort()


print('The medium is ',medium)
