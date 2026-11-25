// THE WORLD TODAY — news-image-20261125 entry point.
//
// The front page is drawn ahead of time by render.py into entry.png;
// this program only proves the PNG is whole and within the bounty
// limits (1024x1024, at most 1 MiB, every chunk CRC valid) and then
// places it where the harness asks via $MAKEFUN_OUTPUT_DIR.

import { crc32 } from "node:zlib";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const SIDE = 1024;
const BYTE_CAP = 1024 * 1024;

function die(reason: string): never {
  console.error(`entry.png failed validation: ${reason}`);
  process.exit(1);
}

function verifyPng(png: Buffer): void {
  if (png.length < 8 || !png.subarray(0, 8).equals(PNG_MAGIC)) {
    die("missing PNG signature");
  }
  if (png.length > BYTE_CAP) {
    die(`file is ${png.length} bytes, over the 1 MiB cap`);
  }
  let cursor = 8;
  let seenHeader = false;
  let seenEnd = false;
  while (cursor + 12 <= png.length) {
    const chunkLen = png.readUInt32BE(cursor);
    const chunkType = png.toString("ascii", cursor + 4, cursor + 8);
    const payloadEnd = cursor + 8 + chunkLen;
    if (payloadEnd + 4 > png.length) {
      die(`chunk ${chunkType} overruns the file`);
    }
    const expected = png.readUInt32BE(payloadEnd);
    const actual = crc32(png.subarray(cursor + 4, payloadEnd));
    if (expected !== actual) {
      die(`chunk ${chunkType} has a bad CRC`);
    }
    if (chunkType === "IHDR") {
      seenHeader = true;
      const w = png.readUInt32BE(cursor + 8);
      const h = png.readUInt32BE(cursor + 12);
      const depth = png[cursor + 16];
      const colourType = png[cursor + 17];
      if (w !== SIDE || h !== SIDE) {
        die(`image is ${w}x${h}, expected ${SIDE}x${SIDE}`);
      }
      if (depth !== 8 || (colourType !== 2 && colourType !== 6)) {
        die(`unexpected colour setup: depth ${depth}, type ${colourType}`);
      }
    }
    cursor = payloadEnd + 4;
    if (chunkType === "IEND") {
      seenEnd = true;
      break;
    }
  }
  if (!seenHeader) {
    die("no IHDR chunk");
  }
  if (!seenEnd) {
    die("no IEND chunk — file is truncated");
  }
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "./output";
const png = readFileSync("entry.png");
verifyPng(png);
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync("entry.png", target);
const written = statSync(target).size;
if (written !== png.length) {
  die(`copied ${written} bytes, expected ${png.length}`);
}
console.log(`entry.png OK: ${SIDE}x${SIDE}, ${png.length} bytes -> ${target}`);
