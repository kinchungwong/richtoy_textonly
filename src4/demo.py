from src4.map_design_table import MapDesignTable, Street, Crossroad


def print_blank_lines_with_delay():
    import time
    for k in range(2):
        time.sleep(0.5)
        s = "_" if k == 0 else ""
        print(f"{s}\r\n")


if __name__ == "__main__":

    print_blank_lines_with_delay()

    table = MapDesignTable()
    cr1 = table.add_crossroad()
    cr2 = table.add_crossroad()
    cr3 = table.add_crossroad()
    cr4 = table.add_crossroad()
    cr5 = table.add_crossroad()
    s12 = table.add_street(Street(cr_from = cr1, cr_to = cr2))
    s23 = table.add_street(Street(cr_from = cr2, cr_to = cr3))
    s34 = table.add_street(Street(cr_from = cr3, cr_to = cr4))
    s45 = table.add_street(Street(cr_from = cr4, cr_to = cr5))
    s51 = table.add_street(Street(cr_from = cr5, cr_to = cr1))
    s13 = table.add_street(Street(cr_from = cr1, cr_to = cr3))
    s24 = table.add_street(Street(cr_from = cr2, cr_to = cr4))
    s35 = table.add_street(Street(cr_from = cr3, cr_to = cr5))
    s41 = table.add_street(Street(cr_from = cr4, cr_to = cr1))
    s52 = table.add_street(Street(cr_from = cr5, cr_to = cr2))
    print(table.crossroads)
    print(table.streets)
    print(table.streets[0])
    print(cr1.streets)

    ### The following code runs fine, because it is idempotent
    ### (the street is already added and has the same specified index) 
    # cr1.streets.add(0, table.streets[0]) 

    ### The following code should raise, because it is trying to
    ### change the item at index[0] to something that isn't equal
    ### to the object that's there (the original streets[0])
    # cr1.streets.add(0, table.streets[1])
