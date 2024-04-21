# Libraries import

from timeit import default_timer as timer
import os
import random

try:
    import termcolor
    import argparse
    import psutil
    import subprocess
except:
    if (os.system("pip install termcolor argparse psutil")):
        print("Failed to install packages, exiting...")
        exit(1)
finally:
    import termcolor
    import argparse
    import psutil
    import subprocess

# Some additional stuff

def crash(msg: str) -> None:
    print(termcolor.colored(msg, "red"))
    exit(1)

def execute(command: str) -> int:
    process = subprocess.Popen(command, shell=True)

    max_mem = 0
    subproc = psutil.Process(process.pid)
    while (process.poll() is None):
        try:
            memory = 0
            for proc in subproc.children(recursive=True):
                memory += proc.memory_info().rss
            memory += subproc.memory_info().rss
            if (memory > max_mem): max_mem = memory
        except:
            a = 0
    return max_mem / 1024 / 1024

def do_cleanup() -> None:
    os.system("rm -rf sources libmain*")

class Lang:
    def __init__(self, lang, gen_time, compile_time) -> None:
        self.lang = lang
        self.gen_time = gen_time
        self.compile_time = compile_time
        self.max_mem_mb = 0
    
    def do_rounding(self) -> None:
        self.gen_time = round(float(self.gen_time), 2)
        self.compile_time = round(float(self.compile_time), 2)
        self.max_mem_mb = round(float(self.max_mem_mb), 2)

# Line generators

def generate_code_line(i: int, line: str) -> str:
    return line % (i, random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF))

# Supported languages list
supported_languages = ['c', 'cpp', 'asm', 'rust', 'zig', 'linker']
# List of lang objects to make statistics at the end
langs = []
compiler_checks = {
    "c": "$(which gcc) -v 2> /dev/null",
    "cpp": "$(which g++) -v 2> /dev/null",
    "asm": "$(which nasm) -v 2> /dev/null",
    "rust": "$(which cargo) -V 2> /dev/null",
    "zig": "zig 2> /dev/null",
    "linker": "ld -v 2> /dev/null"
}
compile_command_assoc = {
    "c": "gcc -shared sources/c/main.c -o sources/c/main.so 2> /dev/null",
    "cpp": "g++ -shared sources/cpp/main.cpp -o sources/cpp/main.so 2> /dev/null",
    "asm": "nasm sources/asm/main.asm -f elf64 -o sources/asm/main.o 2> /dev/null",
    "rust": "cargo build --release --manifest-path sources/rust/Cargo.toml 2> /dev/null",
    "zig": "zig build-lib sources/zig/main.zig 2> /dev/null",
    "linker": "gcc sources/linker/*.o -o sources/linker/main.so -shared 2> /dev/null"
}
source_line_assoc = {
    "c": "long cfunc%d(void){return (long)%d + (long)%d;}\n",
    "cpp": "long cppfunc%d(void){return (long)%d + (long)%d;}\n",
    "asm": "label%d: SUM %d, %d\n",
    "rust": "pub fn func%d() -> usize{%d + %d}\n",
    "zig": "export fn func%d() i64 {return %d + %d;}\n",
}

nice_lang_name_assoc = {
    "c": "C",
    "cpp": "C++",
    "asm": "Assembly",
    "rust": "Rust",
    "zig": "Zig",
    "linker": "LD"
}

# Start source lines
asm_start_source = ["%macro SUM 2\n",
                    "    mov rax, %1\n", 
                    "    mov rbx, %2\n", 
                    "    add rax, rbx\n", 
                    "%endmacro\n"]
rust_start_source = ["fn main(){}\n"]

def validate_languages(languages_to_bench: list) -> None:
    for lang in languages_to_bench:
        if (lang not in supported_languages):
            raise NotImplementedError(f"Language {lang} is not implemented")

def check_compilers(langs: list[str]) -> None:
    for lang in langs:
        if (os.system(compiler_checks[lang])):
            crash("Compiler for language %s not found!" % (nice_lang_name_assoc[lang]))
    
def create_directories_structure() -> None:
    os.mkdir("sources")
    for lang in supported_languages:
        os.mkdir(f"sources/{lang}")

# Generators

def generate_sources(lang: str, linecount: int) -> float:
    start = timer()
    source = open(f"sources/{lang}/main.{lang}", "w")
    if (lang == "asm"):
        source.writelines(asm_start_source)
    elif (lang == "rust"):
        source.close()
        os.system("rm -rf sources/rust")
        os.system("cargo new sources/rust --lib > /dev/null")
        source = open("sources/rust/src/main.rs", "w")
        source.writelines(rust_start_source)
    if (lang != "linker"):
        for i in range(linecount):
            source.write(generate_code_line(i, source_line_assoc[lang]))
    else:
        source.close()
        funcnum = 0
        for i in range(100):
            source = open("sources/linker/main%d.c" % i, "w")
            for _ in range(linecount):
                source.write(generate_code_line(funcnum, source_line_assoc["c"]))
                funcnum += 1
            source.close()
    if (not source.closed):
        source.close()
    end = timer()
    print(termcolor.colored(f"[ GEN ]: Generated {linecount} lines for language {nice_lang_name_assoc[lang]}", "green"))
    return end - start

# Compilers

def compile_sources(lang: str) -> tuple[float, int]:
    start = timer()
    if (lang == "linker"):
        for i in range(100):
            os.system("gcc %s%d.c -c -o %s%d.o" % ("sources/linker/main", i, "sources/linker/main", i))
            start = timer()
            max_mem_mb = execute(compile_command_assoc[lang])
    else:
        max_mem_mb = execute(compile_command_assoc[lang])
    end = timer()
    print(termcolor.colored(f"[ COM ]: Compiled source for language {nice_lang_name_assoc[lang]}", "green"))
    return (end - start, max_mem_mb)

# Entry point

def main():
    parser = argparse.ArgumentParser(description="Compilation benchmark")
    parser.add_argument("--languages", type=str, default=','.join(supported_languages), help="List of languages to bench")
    parser.add_argument("--lines", type=int, default=100000, help="Count of lines to generate")
    args = parser.parse_args()
    languages_to_bench = args.languages.split(',')
    validate_languages(languages_to_bench)
    check_compilers(languages_to_bench)
    create_directories_structure()
    for lang in languages_to_bench:
        langobj = Lang(nice_lang_name_assoc[lang], 0, 0)
        langobj.gen_time = generate_sources(lang, args.lines)
        langobj.compile_time, langobj.max_mem_mb = compile_sources(lang)
        langs.append(langobj)
    do_cleanup()
    print()
    for langobj in langs:
        langobj.do_rounding()
        print(termcolor.colored(f"Statistics of language {langobj.lang}:", "green"))
        print(termcolor.colored(f"    Code generation time: {langobj.gen_time}s", "green"))
        print(termcolor.colored(f"    Code compilation time: {langobj.compile_time}s", "green"))
        print(termcolor.colored(f"    Maximum memory consumption: {langobj.max_mem_mb}MB\n", "green"))
    

if __name__ == "__main__":
    main()
