
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader

reader = vtkXMLPolyDataReader()
reader.SetFileName("Huca0506660.vtp")
reader.Update()

poly = reader.GetOutput()
pd = poly.GetPointData()

print("Número de arrays:", pd.GetNumberOfArrays())
for i in range(pd.GetNumberOfArrays()):
    print(i, pd.GetArrayName(i))