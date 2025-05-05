# psencode
Use Python to encode for PowerShell
A simple Python tool for converting PowerShell to and from the UTF‑16LE Base64 format used by -EncodedCommand. Accepts input from text, files, or stdin and outputs a clean, one-line result ready for use.

## Usage

Encode
```bash
./psencode.py -e "Get-Process | Out-String"
```

Or pipe from a file:
```bash
cat payload.ps1 | ./psencode.py > encoded.txt
```

Decode
```bash
./psencode.py -d "Base64Here" > decoded.ps1
```

## Notes
Input can come from a string, file (-f), or stdin.

If no flags are set and input is piped in, it encodes by default.

Output goes to stdout unless -o is used.
