# Libraries import

from timeit import default_timer as timer
import termcolor
import argparse
import os
import random
import psutil
import subprocess

# Some additional stuff

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
    def __init__(self, lang, gen_time, compile_time):
        self.lang = lang
        self.gen_time = gen_time
        self.compile_time = compile_time
        self.max_mem_mb = 0

# Supported languages list
supported_languages = ['c', 'cpp', 'asm', 'rust', 'zig']
# List of lang objects to make statistics at the end
langs = []
# Compilation commands
c_compile_command = "gcc -shared sources/c/main.c -o sources/c/main.so"
cpp_compile_command = "g++ -shared sources/cpp/main.cpp -o sources/cpp/main.so"
asm_compile_command = "nasm sources/asm/main.asm -f elf64 -o sources/asm/main.o"
rust_compile_command = "cargo build --release --manifest-path sources/rust/Cargo.toml"
zig_compile_command = "zig build-lib sources/zig/main.zig"
# Source lines
asm_start_source = ["%macro SUM 2\n",
                    "    mov rax, %1\n", 
                    "    mov rbx, %2\n", 
                    "    add rax, rbx\n", 
                    "%endmacro\n"]
rust_start_source = ["fn main(){}\n"]
c_source_line = "long cfunc%d(void){return (long)%d + (long)%d;}\n"
cpp_source_line = "long cppfunc%d(void){return (long)%d + (long)%d;}\n"
asm_source_line = "label%d: SUM %d, %d\n"
rust_source_line = "pub fn func%d() -> usize{%d + %d}\n"
zig_source_line = "export fn func%d() i64 {return %d + %d;}\n"

def validate_languages(languages_to_bench: list) -> None:
    for lang in languages_to_bench:
        if (lang not in supported_languages):
            raise NotImplementedError(f"Language {lang} is not implemented")

def create_directories_structure() -> None:
    os.mkdir("sources")
    for lang in supported_languages:
        os.mkdir(f"sources/{lang}")

def nice_lang_name(lang: str) -> str:
    if (lang == "c"): return "C"
    elif (lang == "cpp"): return "C++"
    elif (lang == "asm"): return "Assembly"
    elif (lang == "rust"): return "Rust"
    elif (lang == "zig"): return "Zig"

# Line generators

def generate_c_line(i: int) -> str:
    return c_source_line % (i, random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF))

def generate_cpp_line(i: int) -> str:
    return cpp_source_line % (i, random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF))

def generate_asm_line(i: int) -> str:
    return asm_source_line % (i, random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF))

def generate_rust_line(i: int) -> str:
    return rust_source_line % (i, random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF))

def generate_zig_line(i: int) -> str:
    return zig_source_line % (i, random.randint(0, 0xFFFFFFFF), random.randint(0, 0xFFFFFFFF))

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
    for i in range(linecount):
        if (lang == "c"):
            source.write(generate_c_line(i))
        elif (lang == "cpp"):
            source.write(generate_cpp_line(i))
        elif (lang == "asm"):
            source.write(generate_asm_line(i))
        elif (lang == "rust"):
            source.write(generate_rust_line(i))
        elif (lang == "zig"):
            source.write(generate_zig_line(i))
    source.close()
    end = timer()
    print(termcolor.colored(f"[ GEN ]: Generated {linecount} lines for language {nice_lang_name(lang)}", "green"))
    return end - start

# Compilers

def compile_sources(lang: str) -> Tuple[float, int]:
    start = timer()
    max_mem_mb = 0
    if (lang == "c"):
        max_mem_mb = execute(c_compile_command)
    elif (lang == "cpp"):
        max_mem_mb = execute(cpp_compile_command)
    elif (lang == "asm"):
        max_mem_mb = execute(asm_compile_command)
    elif (lang == "rust"):
        max_mem_mb = execute(rust_compile_command)
    elif (lang == "zig"):
        max_mem_mb = execute(zig_compile_command)
    end = timer()
    print(termcolor.colored(f"[ COM ]: Compiled source for language {nice_lang_name(lang)}", "green"))
    return (end - start, max_mem_mb)

# Benchmarks

# Entry point

def main():
    parser = argparse.ArgumentParser(description="Compilation benchmark")
    parser.add_argument("--languages", type=str, default=','.join(supported_languages), help="List of languages to bench")
    parser.add_argument("--lines", type=int, default=100000, help="Count of lines to generate")
    args = parser.parse_args()
    languages_to_bench = args.languages.split(',')
    validate_languages(languages_to_bench)
    create_directories_structure()
    current_path = os.getcwd()
    for lang in languages_to_bench:
        langobj = Lang(nice_lang_name(lang), 0, 0)
        langobj.gen_time = generate_sources(lang, args.lines)
        langobj.compile_time, langobj.max_mem_mb = compile_sources(lang)
        langs.append(langobj)
    do_cleanup()
    print()
    for langobj in langs:
        print(termcolor.colored(f"Statistics of language {langobj.lang}:", "green"))
        print(termcolor.colored(f"    Code generation time: {langobj.gen_time}", "green"))
        print(termcolor.colored(f"    Code compilation time: {langobj.compile_time}", "green"))
        print(termcolor.colored(f"    Maximum memory consumption: {langobj.max_mem_mb}MB\n", "green"))
    

if __name__ == "__main__":
    main()
