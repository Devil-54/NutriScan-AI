import 'parser_remote_datasource.dart';

class ParserRepository {
  ParserRepository(this._remote);
  final ParserRemoteDatasource _remote;

  Future<List<String>> parseIngredients(String ocrText) => _remote.parseIngredients(ocrText);
}
