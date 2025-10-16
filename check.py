from netCDF4 import Dataset
try:
    file = Dataset("D:\JANU\ISRO\December 2023 data\E06OCML4AC_2023-12-02.nc", "r")
    print(file.variables)
    file.close()
except Exception as e:
    print(f"Error in file: {e}")
