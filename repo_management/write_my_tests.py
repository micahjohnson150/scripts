from netCDF4 import Dataset

def write_tests(filename,file_alias):
    lines = []
    ds = Dataset(filename)

    for var in ds.variables:
        if var not in ['time','x','y']:
            if '_' in var:
                name = ' '.join((var.split('_')))
            else:
                name = var

            lines.append('\n')
            lines.append('\tdef test_{0}(self):\n'.format(var))
            lines.append('\t\t"""\n')
            lines.append('\t\tCheck the simulated {0} is the same as the gold file\n'.format(name))
            lines.append('\t\t"""\n')
            lines.append('\t\ta = compare_image("{0}", self.output_{1},self.gold_{1})\n'.format(var,file_alias))
            lines.append('\t\tassert(a)\n')
    ds.close()
    return lines


with open('./tests/test_awsm.py') as fp:
    lines = fp.readlines()
    fp.close()

lines+=write_tests('./tests/RME/gold/normal_snow.nc','snow')
lines+=write_tests('./tests/RME/gold/normal_em.nc','em')
lines.append( "\nif __name__ == '__main__':\n")
lines.append("\tunittest.main()\n")

with open('./test.py','w+') as fp:
    fp.writelines(lines)
    fp.close()
