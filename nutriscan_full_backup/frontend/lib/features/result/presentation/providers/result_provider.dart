import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/services/api_service.dart';
import '../../data/ocr_remote_datasource.dart';
import '../../data/ocr_repository.dart';
import '../../data/parser_remote_datasource.dart';
import '../../data/parser_repository.dart';
import '../../data/recommendation_remote_datasource.dart';
import '../../data/recommendation_repository.dart';

final ocrRepositoryProvider = Provider<OcrRepository>((ref) {
  return OcrRepository(OcrRemoteDatasource(ref.watch(apiServiceProvider)));
});

final parserRepositoryProvider = Provider<ParserRepository>((ref) {
  return ParserRepository(ParserRemoteDatasource(ref.watch(apiServiceProvider)));
});

final recommendationRepositoryProvider = Provider<RecommendationRepository>((ref) {
  return RecommendationRepository(RecommendationRemoteDatasource(ref.watch(apiServiceProvider)));
});
