# import module
from pdf2image import convert_from_path
import os


def convertir_pdf(filename):
    # Store Pdf with convert_from_path function
    images = convert_from_path('./pdf/' + filename)

    for i in range(len(images)):

        if (os.path.exists("./img/" + filename[:-4]) == False):
            os.mkdir("./img/" + filename[:-4])

        # Save pages as images in the pdf
        images[i].save("./img/" + filename[:-4] + "/" + filename[:-4] + str(i) + '.png', 'PNG')


if __name__ == "__main__":
    convertir_pdf("factura1.pdf")
