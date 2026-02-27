def celcius_to_fahrenheit(c):
   return (c * 9/5)+ 32

def fahrenheit_to_celcius(f):
   return (f-32)*5/9

#Test both functions
c=15
f=celcius_to_fahrenheit(c)
print(f"{c}°C is: {f}°F")


f=59
c=fahrenheit_to_celcius(f)
print(f"{f}°F is: {c}°C")
