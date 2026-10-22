import '../../../core/services/api_service.dart';
import 'profile_model.dart';

class ProfileRemoteDatasource {
  ProfileRemoteDatasource(this._api);
  final ApiService _api;

  Future<FullProfileModel> getProfile() async {
    final res = await _api.get('/profile/me');
    return FullProfileModel.fromJson(res['data'] as Map<String, dynamic>);
  }

  Future<HealthProfileModel> updateProfile(HealthProfileModel profile) async {
    final res = await _api.put('/profile/me', data: profile.toUpdateJson());
    return HealthProfileModel.fromJson(res['data'] as Map<String, dynamic>);
  }
}
