#!/Users/mfdutra/py/pypdf/bin/python3

# Reorder a PDF's pages into saddle-stitch booklet imposition order,
# ready for 2-up duplex printing in macOS Preview.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# In macOS Preview, print the resulting PDF with:
#   Layout > Pages per Sheet: 2
#   Two-Sided: On, binding on the short edge
# Then stack the printed sheets in order and fold once down the middle.

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def booklet_order(num_pages):
    """Return the 0-indexed page order for booklet imposition.

    None marks a blank filler page, used when num_pages isn't a
    multiple of 4.
    """
    padded = -(-num_pages // 4) * 4
    pages = list(range(num_pages)) + [None] * (padded - num_pages)

    order = []
    for i in range(padded // 4):
        front_left = pages[padded - 1 - 2 * i]
        front_right = pages[2 * i]
        back_left = pages[2 * i + 1]
        back_right = pages[padded - 2 - 2 * i]
        order.extend([front_left, front_right, back_left, back_right])
    return order


def parse_args():
    parser = argparse.ArgumentParser(
        description='Reorder a PDF into booklet imposition order.')
    parser.add_argument('input', type=Path, help='input PDF file')
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = args.input
    output_path = input_path.with_stem(input_path.stem + '_booklet')

    reader = PdfReader(input_path)
    if not reader.pages:
        sys.exit(f'{input_path} has no pages')

    writer = PdfWriter()
    box = reader.pages[0].mediabox

    for index in booklet_order(len(reader.pages)):
        if index is None:
            writer.add_blank_page(width=box.width, height=box.height)
        else:
            writer.add_page(reader.pages[index])

    with open(output_path, 'wb') as f:
        writer.write(f)

    print(f'Wrote {output_path}: {len(writer.pages)} pages '
          f'(from {len(reader.pages)}-page {input_path})')


if __name__ == '__main__':
    main()
