def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    return length * width


def main():
    length = 5
    width = 10

    area = calculate_area(length, width)

    print("Length:", length)
    print("Width:", width)
    print("Area:", area)


if __name__ == "__main__":
    main()