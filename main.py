#!/usr/bin/env python3
import argparse
import db
import models


def cmd_init(args):
    db.init_db()
    print("Base de datos inicializada.")


def cmd_add(args):
    available = args.available.lower() in ("1", "y", "yes", "true", "si", "s")
    room = models.add_room(args.number, args.type, args.price, available, args.notes)
    print(f"Habitación registrada: {room}")


def cmd_list(args):
    rooms = models.list_rooms()
    if not rooms:
        print("No hay habitaciones.")
        return
    for r in rooms:
        print(r)


def cmd_get(args):
    r = models.get_room_by_number(args.number)
    if not r:
        print("No encontrada")
    else:
        print(r)


def cmd_update(args):
    fields = {}
    if args.type:
        fields["type"] = args.type
    if args.price is not None:
        fields["price"] = args.price
    if args.available is not None:
        fields["available"] = args.available.lower() in ("1", "y", "yes", "true", "si", "s")
    if args.notes is not None:
        fields["notes"] = args.notes
    r = models.update_room(args.number, **fields)
    if not r:
        print("No encontrada")
    else:
        print("Actualizada:", r)


def cmd_delete(args):
    ok = models.delete_room(args.number)
    print("Eliminada." if ok else "No encontrada.")


def cmd_set_availability(args):
    available = args.available.lower() in ("1", "y", "yes", "true", "si", "s")
    r = models.set_availability(args.number, available)
    if not r:
        print("No encontrada")
    else:
        print("Disponibilidad cambiada:", r)


def cmd_list_by_type(args):
    rooms = models.list_by_type(args.type)
    if not rooms:
        print("No hay habitaciones de ese tipo.")
        return
    for r in rooms:
        print(r)


def main():
    parser = argparse.ArgumentParser(description="Gestión de habitaciones - Hotel")
    sub = parser.add_subparsers(dest="cmd")

    sub_init = sub.add_parser("init", help="Inicializar la base de datos")
    sub_init.set_defaults(func=cmd_init)

    p = sub.add_parser("add", help="Agregar habitación")
    p.add_argument("--number", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--available", default="yes")
    p.add_argument("--notes", default=None)
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="Listar habitaciones")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("get", help="Consultar por número")
    p.add_argument("--number", required=True)
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("update", help="Modificar habitación")
    p.add_argument("--number", required=True)
    p.add_argument("--type")
    p.add_argument("--price", type=float)
    p.add_argument("--available")
    p.add_argument("--notes")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("delete", help="Eliminar habitación")
    p.add_argument("--number", required=True)
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("set-availability", help="Cambiar disponibilidad")
    p.add_argument("--number", required=True)
    p.add_argument("--available", required=True)
    p.set_defaults(func=cmd_set_availability)

    p = sub.add_parser("list-by-type", help="Listar por tipo")
    p.add_argument("--type", required=True)
    p.set_defaults(func=cmd_list_by_type)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
