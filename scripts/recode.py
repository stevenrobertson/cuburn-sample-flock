import subprocess, os, sys

def main(src, dst):
    for frag, dirs, files in os.walk(src):
        mtimes = [os.path.getmtime(os.path.join(frag, f))
                  for f in files if f.endswith('.h264')]
        if not mtimes: continue
        dst_dir = os.path.join(dst, os.path.relpath(frag, src))
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        dst_file = os.path.join(dst_dir, '00001.h264')
        if (os.path.isfile(dst_file) and
            os.path.getmtime(dst_file) > max(mtimes)):
            continue
        dst_tmp = dst_file + '.tmp'
        sub = subprocess.Popen('avconv -r 30 -i - -c:v libx264 '
            '-crf 16 -pix_fmt yuv420p -y -f h264'.split() + [dst_tmp],
            stdin=subprocess.PIPE)
        for f in sorted([os.path.join(frag, f) for f in files]):
            if f.endswith('.h264'):
                sub.stdin.write(open(f).read())
        sub.stdin.close()
        if sub.wait() != 0:
            raise ValueError('error')
        os.rename(dst_tmp, dst_file)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
