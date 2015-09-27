import sys
import zipfile
import os

def main():
    zip_fn = sys.argv[1]
    output_dir = sys.argv[2]
    zf = zipfile.ZipFile(zip_fn)
    print 'reading in', zip_fn
    for info in zf.infolist():
        data = zf.read(info.filename)
        output_file = os.path.join(output_dir, os.path.basename(info.filename))
        print 'writing out to', output_file
        writer = open(output_file, 'w')
        writer.write(data + '\n')
        writer.close()



if __name__ == '__main__':
    sys.exit(main())
